import hashlib

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from mentor.config import ROOT, settings
from mentor.models import embedding_identity, embedding_model


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()[:20]


def item_text(item):
    return "\n".join(f"{key}: {item[key]}" for key in
                     ["name", "category", "level", "description", "keywords", "url"])


class Store:
    def __init__(self, path=None, embeddings=None, identity=None):
        self.embeddings = embeddings
        self.identity = identity or embedding_identity()
        self.client = chromadb.PersistentClient(path=str(path or ROOT / "storage" / "chroma"))
        suffix = digest(self.identity)
        self.meta = self.client.get_or_create_collection(
            "android_meta_" + suffix, embedding_function=None, metadata={"hnsw:space": "cosine"})
        self.docs = self.client.get_or_create_collection(
            "android_docs_" + suffix, embedding_function=None, metadata={"hnsw:space": "cosine"})

    def embedder(self):
        return self.embeddings or embedding_model()

    def index_items(self, items):
        texts = [item_text(item) for item in items]
        vectors = self.embedder().embed_documents(texts)
        self.meta.upsert(ids=[item["id"] for item in items], documents=texts,
                         embeddings=vectors, metadatas=[dict(item, source_type="항목 메타데이터") for item in items])
        active = {item["id"] for item in items}
        obsolete = [identifier for identifier in self.meta.get()["ids"] if identifier not in active]
        if obsolete:
            self.meta.delete(ids=obsolete)
        return self.meta.count()

    def index_document(self, item, document, cfg=None):
        cfg = cfg or settings()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_text(document["text"])
        if not chunks:
            return 0
        group = item["id"] + ":" + digest(document["url"])
        fingerprint = digest(document["text"] + f":{cfg.chunk_size}:{cfg.chunk_overlap}:" + self.identity)
        ids = [f"{group}:{fingerprint}:{index}" for index in range(len(chunks))]
        old = self.docs.get(where={"group_id": group})["ids"]
        if set(old) == set(ids):
            return len(ids)
        vectors = self.embedder().embed_documents(chunks)
        metadata = {key: value for key, value in document.items() if key != "text" and isinstance(value, (str, int, float, bool))}
        metadata.update(item_id=item["id"], item_name=item["name"], group_id=group, source_type="외부 문서")
        self.docs.upsert(ids=ids, documents=chunks, embeddings=vectors,
                         metadatas=[dict(metadata, chunk_index=index) for index in range(len(chunks))])
        stale = list(set(old) - set(ids))
        if stale:
            self.docs.delete(ids=stale)
        return len(ids)

    def retrieve(self, item_id, question, cfg=None):
        cfg = cfg or settings()
        evidence = []
        selected = self.meta.get(ids=[item_id], include=["documents", "metadatas"])
        if selected["ids"]:
            evidence.append({"text": selected["documents"][0], **selected["metadatas"][0]})
        available = self.docs.get(where={"item_id": item_id}, include=[])["ids"]
        if available:
            result = self.docs.query(
                query_embeddings=[self.embedder().embed_query(question)],
                where={"item_id": item_id}, n_results=min(cfg.top_k, len(available)),
                include=["documents", "metadatas", "distances"],
            )
            for text, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
                if distance <= cfg.max_distance:
                    evidence.append({"text": text, **metadata})
        unique, seen = [], set()
        for row in evidence:
            key = digest(row["text"])
            if key not in seen:
                seen.add(key)
                unique.append(row)
        return unique

    def search_items(self, condition, limit=12):
        if not self.meta.count():
            return []
        result = self.meta.query(query_embeddings=[self.embedder().embed_query(condition)],
                                 n_results=min(limit, self.meta.count()), include=["metadatas"])
        return result["metadatas"][0]
