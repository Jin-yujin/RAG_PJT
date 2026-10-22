import hashlib
from dataclasses import replace
from types import SimpleNamespace

import pytest

from mentor.collector import extract_document, validate_url
from mentor.config import MentorError, Settings, catalog
from mentor.llm import parse_object
from mentor.pipeline import build_graph, citations
from mentor.store import Store


class TestEmbeddings:
    """DB 동작 검사 전용. 실제 의미 검색 모델이 아닙니다."""
    __test__ = False

    def embed_documents(self, texts):
        return [[(v + 1) / 256 for v in hashlib.sha256(text.encode()).digest()[:16]] for text in texts]

    def embed_query(self, text):
        return self.embed_documents([text])[0]


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "chroma", embeddings=TestEmbeddings(), identity="test-only")


def document(text="ViewModel keeps UI state. " * 80):
    return {"title": "Test reference", "url": "https://developer.android.com/test", "text": text,
            "author": "Fixture, not official data", "license": "test fixture", "license_url": "https://example.com/license"}


def test_catalog_contains_100_distinct_real_target_urls():
    items = catalog()
    assert len(items) >= 100
    assert len({item["id"] for item in items}) == len(items)
    assert len({item["url"] for item in items}) == len(items)
    for item in items:
        validate_url(item["url"])


def test_metadata_upsert_is_idempotent(store):
    items = catalog()[:2]
    assert store.index_items(items) == 2
    assert store.index_items(items) == 2


def test_document_upsert_chunk_setting_and_item_isolation(store):
    a, b = catalog()[:2]
    store.index_items([a, b])
    cfg = Settings(chunk_size=220, chunk_overlap=20, max_distance=2)
    first = store.index_document(a, document(), cfg)
    assert first > 1
    assert store.index_document(a, document(), cfg) == first
    assert store.docs.count() == first
    store.index_document(b, document(), cfg)
    assert store.docs.count() == first * 2
    changed = store.index_document(a, document(), replace(cfg, chunk_size=400))
    assert changed < first
    assert store.docs.count() == changed + first
    rows = store.retrieve(a["id"], "ViewModel", cfg)
    assert rows[0]["id"] == a["id"]
    assert all(row["item_id"] == a["id"] for row in rows if row["source_type"] == "외부 문서")


def test_actual_citations_only():
    evidence = [{"title": "a"}, {"title": "b"}]
    cited, invalid = citations("설명 [근거 2] [근거 2] [근거 99]", evidence)
    assert [row["title"] for row in cited] == ["b"]
    assert invalid == [99]


def test_graph_does_not_generate_from_metadata_only(store):
    item = catalog()[0]
    store.index_items([item])
    def forbidden(*args):
        raise AssertionError("No external evidence means no model generation")
    result = build_graph(store, responder=forbidden).invoke({"item_id": item["id"], "question": "unknown"})
    assert "확인되지" in result["answer"]
    assert result["cited"] == []


def test_graph_nodes_and_invalid_citation_guard():
    fake = SimpleNamespace(retrieve=lambda *args: [{"source_type": "외부 문서", "text": "fact", "title": "source"}])
    graph = build_graph(fake, responder=lambda *args: "fact [근거 99]")
    assert {"retrieve", "generate"} <= set(graph.get_graph().nodes)
    result = graph.invoke({"item_id": "x", "question": "test"})
    assert result["invalid_citations"] == [99]
    assert result["cited"] == []


def test_json_and_config_validation():
    assert parse_object('```json\n{"queries": ["ViewModel"]}\n```')["queries"] == ["ViewModel"]
    with pytest.raises(MentorError):
        parse_object("not json")
    with pytest.raises(MentorError):
        Settings(chunk_size=100, chunk_overlap=100)


def test_extraction_preserves_attribution_and_removes_code():
    html = '<h1>Title</h1><div class="devsite-article-body"><p>' + 'Useful prose. ' * 15 + '</p><pre>secret code</pre><p>Copyright Example</p></div><a href="https://creativecommons.org/licenses/by/4.0/">license</a>'
    doc = extract_document(html, "https://developer.android.com/test")
    assert "secret code" not in doc["text"]
    assert "Copyright Example" in doc["notices"]
    assert doc["license"] == "CC BY 4.0"


@pytest.mark.parametrize("url", ["http://developer.android.com/test", "https://evil.example/test", "https://developer.android.com@evil.example/test", "https://developer.android.com/reference/java/lang/String"])
def test_url_allowlist(url):
    with pytest.raises(MentorError):
        validate_url(url)
