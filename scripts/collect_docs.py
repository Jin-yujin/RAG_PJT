"""허용 목록의 원문을 수집합니다. 기본 3개, --limit 112로 전체 수집."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mentor.collector import Collector
from mentor.config import MentorError, ROOT, catalog, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit은 1 이상입니다.")
    # 수집 단계에서는 임베딩 모델이나 GMS 키가 필요하지 않습니다.
    collector = Collector(store=None)
    rows = []
    for item in catalog()[:args.limit]:
        print("수집:", item["name"], flush=True)
        try:
            document, cached = collector.fetch(item["url"])
            rows.append({"item_id": item["id"], "url": item["url"], "status": "ok",
                         "cached": cached, "characters": len(document["text"])})
            print("  완료", "(캐시)" if cached else "(새 원문)", flush=True)
        except MentorError as error:
            rows.append({"item_id": item["id"], "url": item["url"], "status": "failed", "message": str(error)})
            print("  미수집:", str(error), flush=True)
        write_json(ROOT / "data" / "collection_report.json", rows)
    success = sum(row["status"] == "ok" for row in rows)
    print(f"수집 성공 {success}/{len(rows)}. 실패 항목은 완료로 집계하지 않습니다.")
    return 0 if success == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
