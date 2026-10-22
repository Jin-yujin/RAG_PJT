import os
from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from mentor.config import MentorError, ROOT


def chat_ready():
    return all(os.getenv(key, "").strip() for key in
               ["GMS_API_KEY", "GMS_BASE_URL", "GMS_MODEL"])


@lru_cache(maxsize=1)
def chat_model():
    if not chat_ready():
        raise MentorError(".env에 GMS_API_KEY, GMS_BASE_URL, GMS_MODEL을 입력하세요.")
    return ChatOpenAI(
        api_key=os.environ["GMS_API_KEY"],
        base_url=os.environ["GMS_BASE_URL"],
        model=os.environ["GMS_MODEL"],
        timeout=60,
        max_retries=1,
    )


def embedding_identity():
    provider = os.getenv("EMBEDDING_PROVIDER", "local")
    model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    endpoint = os.getenv("EMBEDDING_BASE_URL", "") if provider == "openai" else "cpu"
    return f"{provider}:{model}:{endpoint}"


class LocalEmbeddings(Embeddings):
    def __init__(self, name):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(name, device="cpu", cache_folder=str(ROOT / "storage" / "models"))

    def embed_documents(self, texts):
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]


@lru_cache(maxsize=1)
def embedding_model():
    provider = os.getenv("EMBEDDING_PROVIDER", "local")
    model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    if provider == "local":
        return LocalEmbeddings(model)
    if provider == "openai":
        key = os.getenv("EMBEDDING_API_KEY") or os.getenv("GMS_API_KEY")
        url = os.getenv("EMBEDDING_BASE_URL") or os.getenv("GMS_BASE_URL")
        if not key or not url:
            raise MentorError("임베딩 API의 키와 기본 주소를 설정하세요.")
        return OpenAIEmbeddings(model=model, api_key=key, base_url=url, max_retries=1)
    raise MentorError("EMBEDDING_PROVIDER는 local 또는 openai로 설정하세요.")
