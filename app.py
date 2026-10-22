import time

import streamlit as st

from mentor.collector import Collector
from mentor.config import MentorError, ROOT, catalog, settings
from mentor.models import chat_ready
from mentor.pipeline import build_graph
from mentor.service import explore, learning_question
from mentor.store import Store


st.set_page_config(page_title="Android RAG 멘토", page_icon="📚", layout="wide")
st.title("📚 Android 개발 문서 RAG 멘토")
st.caption("공식 문서에 근거한 비공식 학습 서비스 · Google의 공식 서비스가 아닙니다.")


def show_error(error):
    if isinstance(error, MentorError):
        st.error(str(error))
    else:
        st.error("처리를 완료하지 못했습니다. 설치·네트워크·모델 설정을 확인하세요. 비밀 값과 오류 추적은 화면에 표시하지 않습니다.")


def show_sources(message):
    sources = message.get("sources", [])
    if not sources:
        st.info("이 답변에서 인용한 근거가 없습니다.")
    for source in sources:
        title = source.get("title", source.get("name", "문서"))
        with st.expander(f"[근거 {source['number']}] {title} · {source['source_type']}"):
            st.write(source["text"])
            st.link_button("원문 보기", source["url"])
            st.caption("제공자: " + source.get("author", "Google / Android Developers"))
            st.write("이용 조건:", source.get("license", "문서별 조건 확인"))
            st.link_button("이용 조건 확인", source.get("license_url", "https://developer.android.com/license"))
            st.caption(source.get("changes", "학습 항목 메타데이터 직접 작성"))
            if source.get("collected_at"):
                st.caption("수집일: " + source["collected_at"])
            if source.get("notices"):
                st.text(source["notices"])


try:
    items = catalog()
    store = Store()
    cfg = settings()
except Exception as error:
    show_error(error)
    st.stop()

lookup = {item["id"]: item for item in items}
if "selected_item" not in st.session_state:
    st.session_state.selected_item = items[0]["id"]
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "explore_results" not in st.session_state:
    st.session_state.explore_results = []

if pending := st.session_state.pop("pending_item", None):
    st.session_state.selected_item = pending

with st.sidebar:
    st.header("학습 항목")
    st.selectbox("질문할 항목을 고르세요", options=list(lookup), key="selected_item",
                 format_func=lambda identifier: f"{lookup[identifier]['name']} · {lookup[identifier]['category']}")
    st.metric("항목 메타데이터", len(items))
    st.metric("메타데이터 색인", store.meta.count())
    st.metric("수집된 원문 파일", len(list((ROOT / "data" / "raw").glob("*.json"))))
    st.metric("외부 문서 청크", store.docs.count())
    st.caption(f"청크 {cfg.chunk_size}자 / 중복 {cfg.chunk_overlap}자 / 외부 Top-k {cfg.top_k}")
    st.caption("112건은 직접 작성한 학습 항목이며 공식 원문 수집 건수와 다릅니다.")
    auto_collect = st.checkbox("질문 전에 관련 문서 수집", value=False)
    st.caption("수집은 공식 문서 허용 목록 안에서만 진행됩니다. 이미 받은 원문은 캐시를 사용합니다.")
    if st.button("현재 항목 대화 지우기"):
        st.session_state.chats[st.session_state.selected_item] = []
        st.rerun()

item = lookup[st.session_state.selected_item]
if not chat_ready():
    st.warning(".env의 GMS_API_KEY, GMS_BASE_URL, GMS_MODEL을 입력하세요. 키 없이도 원문 수집과 로컬 색인은 가능합니다.")
if store.meta.count() == 0:
    st.warning("색인이 비어 있습니다. 터미널에서 python scripts/index_data.py를 먼저 실행하세요.")

explore_tab, chat_tab = st.tabs(["조건으로 항목 찾기", "선택 항목 질문"])
with explore_tab:
    st.write("예: ‘화면 상태 관리를 처음 배우고 싶어’, ‘로컬 저장소를 다루는 항목’")
    with st.form("explore"):
        condition = st.text_input("원하는 학습 조건", max_chars=1000)
        search_clicked = st.form_submit_button("조건 검색")
    if search_clicked and condition.strip():
        try:
            with st.spinner("의미 검색 후 조건에 맞는 항목을 선별하는 중..."):
                st.session_state.explore_results = explore(store, condition.strip())
            if not st.session_state.explore_results:
                st.info("현재 메타데이터에서 조건에 맞는 항목을 확인하지 못했습니다.")
        except Exception as error:
            show_error(error)
    for match in st.session_state.explore_results:
        candidate = match["item"]
        with st.container(border=True):
            st.subheader(candidate["name"])
            st.write(candidate["description"])
            st.caption(match["reason"])
            if st.button("이 항목 선택", key="choose_" + candidate["id"]):
                st.session_state.pending_item = candidate["id"]
                st.rerun()

with chat_tab:
    st.subheader(item["name"])
    st.write(item["description"])
    st.link_button("선택 항목 공식 문서", item["url"])
    if st.button("현재 항목 공식 문서 수집·색인"):
        try:
            with st.spinner("원문 확인 → 수집 → 청킹 → 임베딩 → 색인 중..."):
                result = Collector(store).collect_one(item)
            st.success(f"완료: {result['chunks']}개 청크. {'저장된 원문을 재사용했습니다.' if result['cached'] else '원문을 새로 수집했습니다.'}")
        except Exception as error:
            show_error(error)

    history = st.session_state.chats.setdefault(item["id"], [])
    for message in history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                show_sources(message)
                st.caption(f"처리 시간: {message.get('seconds', 0):.1f}초")

    guide_clicked = st.button("📖 근거 기반 학습 가이드 만들기", disabled=not chat_ready() or store.meta.count() == 0)
    question = st.chat_input("선택 항목에 대해 질문하세요", max_chars=2000,
                             disabled=not chat_ready() or store.meta.count() == 0)
    if guide_clicked:
        question = learning_question(item)
    if question and question.strip():
        started = time.monotonic()
        try:
            with st.status("자료를 확인하고 있습니다...", expanded=True) as status:
                if auto_collect:
                    st.write("검색어 추출 및 허용 목록 후보 선별 → 원문 수집·색인")
                    report = Collector(store).collect_for_question(item, question, items)
                    st.write("검색어:", report["queries"])
                    st.write("선별한 항목:", report["selected"])
                    st.write("제외한 후보:", report["rejected"])
                    st.write("검색어 캐시:", report["query_cached"])
                st.write("LangGraph retrieve → generate 실행 중")
                result = build_graph(store).invoke({
                    "item_id": item["id"], "question": question,
                    "history": [{"role": row["role"], "content": row["content"]} for row in history[-6:]],
                })
                status.update(label="답변 생성 완료", state="complete", expanded=False)
            history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": result["answer"], "sources": result["cited"],
                 "seconds": time.monotonic() - started},
            ])
            st.rerun()
        except Exception as error:
            show_error(error)

st.divider()
st.caption("공식 문서 설명을 발췌·분할하고 AI가 요약·재구성합니다. 원문과 이용 조건을 확인하세요. "
           "자동 출처 표시는 인용의 사실적 타당성을 보장하지 않습니다. 대화는 브라우저 세션 안에서만 유지됩니다.")
