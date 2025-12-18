import os
from typing import List, Dict, Any, Tuple

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "docs")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "faiss_index")

def build_or_load_vectorstore() -> FAISS:
    embeddings = OpenAIEmbeddings()
    if os.path.exists(INDEX_DIR):
        return FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)

    docs: List[Document] = []
    for fn in os.listdir(DOCS_DIR):
        if not fn.endswith((".md", ".txt")):
            continue
        path = os.path.join(DOCS_DIR, fn)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        doc_id = os.path.splitext(fn)[0]
        docs.append(Document(page_content=text, metadata={"doc_id": doc_id}))

    splitter = RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=80)
    chunks = splitter.split_documents(docs)
    vs = FAISS.from_documents(chunks, embeddings)
    os.makedirs(INDEX_DIR, exist_ok=True)
    vs.save_local(INDEX_DIR)
    return vs

def retrieve_evidence(
    vs: FAISS,
    query: str,
    k: int = 4,
) -> List[Dict[str, str]]:
    docs = vs.similarity_search(query, k=k)
    out = []
    for d in docs:
        out.append({
            "doc_id": d.metadata.get("doc_id", "unknown"),
            "snippet": d.page_content[:400]
        })
    return out
