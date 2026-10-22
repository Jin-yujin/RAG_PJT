"""허용 목록의 Android 공식 문서만 수집합니다. 검색엔진 전체 검색은 하지 않습니다."""
import os
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from mentor.config import MentorError, ROOT, read_json, settings, write_json
from mentor.llm import keywords, select_candidates
from mentor.store import digest


def validate_url(url):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "developer.android.com" or parsed.username or parsed.password:
        raise MentorError("허용된 Android Developers HTTPS 주소만 수집합니다.")
    if parsed.path.startswith(("/reference/java/", "/reference/javax/", "/reference/android/icu/", "/reference/org/")):
        raise MentorError("별도 라이선스 검토가 필요한 참조 문서는 현재 수집 대상에서 제외합니다.")


def extract_document(html, url):
    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one(".devsite-article-body")
    if body is None:
        raise MentorError("문서 본문을 찾지 못했습니다. 로그인·차단·페이지 구조를 확인하세요.")
    title = soup.select_one("h1")
    title = title.get_text(" ", strip=True).split("컬렉션을 사용해")[0].strip() if title else url
    # 설명 텍스트만 수집합니다. 예제 코드·로고·이미지는 포함하지 않습니다.
    for node in body.select("script, style, nav, pre, img, svg, iframe, video, audio, devsite-code, .devsite-code-buttons"):
        node.decompose()
    text = body.get_text("\n", strip=True)
    if len(text.strip()) < 100:
        raise MentorError("문서 설명이 너무 짧습니다. 정상적인 본문인지 확인하세요.")
    # 개별 페이지의 CC 표시가 있으면 우선합니다. 없으면 Android 문서 기본 정책을 기록합니다.
    licenses = [a.get("href", "") for a in soup.select("a[href]") if "creativecommons.org/licenses/by/" in a.get("href", "")]
    cc = next((link for link in licenses if "/4.0" in link), None)
    cc = cc or next((link for link in licenses if "/2.5" in link), None)
    if cc:
        license_name = "CC BY 4.0" if "/4.0" in cc else "CC BY 2.5"
        license_url = cc
        basis = "수집 페이지의 라이선스 링크. 개별 예외는 별도 검토 필요."
    else:
        license_name = "Apache-2.0 (Android 문서 기본 정책, 별도 고지 우선)"
        license_url = "https://www.apache.org/licenses/LICENSE-2.0"
        basis = "https://developer.android.com/license 의 문서 기본 규칙. 개별 예외는 별도 검토 필요."
    # 명시적 저작권/고지 문구는 별도 필드에도 보존합니다.
    notices = [line for line in soup.get_text("\n", strip=True).splitlines()
               if re.search(r"copyright|©|all rights reserved|except as (?:otherwise )?noted", line, re.I)]
    return {
        "title": title, "url": url, "text": text,
        "author": "Google / Android Open Source Project",
        "license": license_name, "license_url": license_url,
        "license_basis": basis, "notices": "\n".join(notices),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "changes": "설명 텍스트 발췌·청킹. AI 답변에서는 요약·재구성.",
    }


class Collector:
    def __init__(self, store):
        self.store = store
        self.cfg = settings()
        self.last_request = 0.0
        self.robot = None
        self.agent = "AndroidRAGMentor/0.1"
        self.session = requests.Session()
        retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], respect_retry_after_header=True)
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def request(self, url):
        validate_url(url)
        contact = os.getenv("COLLECTOR_CONTACT", "").strip()
        elapsed = time.monotonic() - self.last_request
        time.sleep(max(0, self.cfg.request_interval - elapsed))
        try:
            response = self.session.get(
                url, headers={"User-Agent": (f"{self.agent} (+mailto:{contact})" if contact else self.agent)},
                timeout=self.cfg.request_timeout, allow_redirects=False,
            )
            # 외부 호스트로 자동 이동하지 않습니다. 같은 호스트의 리다이렉트도 확인 후 재요청합니다.
            for _ in range(3):
                if response.status_code not in [301, 302, 303, 307, 308]:
                    break
                target = urljoin(response.url, response.headers.get("Location", ""))
                validate_url(target)
                time.sleep(self.cfg.request_interval)
                response = self.session.get(target, headers={"User-Agent": (f"{self.agent} (+mailto:{contact})" if contact else self.agent)},
                                            timeout=self.cfg.request_timeout, allow_redirects=False)
            response.raise_for_status()
            if 300 <= response.status_code < 400:
                raise MentorError("리다이렉트가 반복되어 수집을 중단했습니다.")
            return response
        except requests.RequestException as error:
            raise MentorError("공식 문서 요청에 실패했습니다. 네트워크·주소·호출 제한을 확인하세요.") from error
        finally:
            self.last_request = time.monotonic()

    def fetch(self, url):
        validate_url(url)
        path = ROOT / "data" / "raw" / (digest(url) + ".json")
        if path.exists():
            return read_json(path), True
        if self.robot is None:
            response = self.request("https://developer.android.com/robots.txt")
            self.robot = RobotFileParser()
            self.robot.parse(response.text.splitlines())
        if not self.robot.can_fetch(self.agent, url):
            raise MentorError("robots.txt에서 허용하지 않는 문서입니다.")
        response = self.request(url)
        if "text/html" not in response.headers.get("Content-Type", ""):
            raise MentorError("HTML 문서가 아닌 응답이므로 수집하지 않았습니다.")
        document = extract_document(response.text, url)
        write_json(path, document)
        return document, False

    def collect_one(self, item):
        document, cached = self.fetch(item["url"])
        count = self.store.index_document(item, document)
        return {"item_id": item["id"], "title": document["title"], "cached": cached, "chunks": count}

    def collect_for_question(self, item, question, items):
        # 선택 항목의 원문은 후보 선별과 길이 기준보다 우선하여 수집합니다.
        mandatory = self.collect_one(item)
        queries = keywords(item, question)
        cache_path = ROOT / "data" / "collection_cache.json"
        cache = read_json(cache_path, {})
        query_key = digest(item["id"] + ":" + "|".join(queries))
        old = cache.get(query_key)
        lookup = {row["id"]: row for row in items}
        # 이전 성공 건은 HTTP 재수집 없이 원문 캐시를 재사용합니다.
        if old:
            reports = [mandatory]
            for identifier in old["selected"]:
                if identifier != item["id"] and identifier in lookup:
                    document, _ = self.fetch(lookup[identifier]["url"])
                    self.store.index_document(item, document)
            return {**old, "query_cached": True, "reports": reports}
        words = set(re.findall(r"[\w.]+", " ".join(queries).lower()))
        def rank(row):
            text = " ".join(str(value) for value in row.values()).lower()
            return sum(word in text for word in words)
        candidates = sorted((row for row in items if row["id"] != item["id"]), key=rank, reverse=True)[:8]
        selected = select_candidates(item, question, candidates)[:max(0, self.cfg.max_selected_documents - 1)]
        reports = [mandatory]
        for identifier in selected:
            # 관련 문서도 현재 선택한 항목에 연결해 저장합니다.
            document, cached = self.fetch(lookup[identifier]["url"])
            count = self.store.index_document(item, document)
            reports.append({"item_id": identifier, "title": document["title"], "cached": cached, "chunks": count})
        record = {"queries": queries, "candidates": [row["id"] for row in candidates],
                  "selected": [item["id"]] + selected,
                  "rejected": [row["id"] for row in candidates if row["id"] not in selected]}
        cache[query_key] = record
        write_json(cache_path, cache)
        return {**record, "query_cached": False, "reports": reports}
