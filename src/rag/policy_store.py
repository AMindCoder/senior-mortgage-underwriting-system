import logging
import re
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import settings
from src.core.llm import get_embeddings

logger = logging.getLogger(__name__)


def _load_documents_from_pdf(pdf_path: str):
    """Load documents from a PDF file using pypdf."""
    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader(pdf_path)
    return loader.load()


def _load_documents_from_text(text_path: str):
    """Load documents from a plain text file as a fallback."""
    from langchain_core.documents import Document

    content = Path(text_path).read_text(encoding="utf-8")
    return [Document(page_content=content, metadata={"source": text_path})]


def create_policy_store() -> Chroma:
    """Create or connect to the ChromaDB vector store with underwriting policies.

    Tries to load policies from PDF first, then falls back to .txt.
    Uses a persistent ChromaDB client when running with docker (CHROMA_HOST set),
    otherwise uses a local persistent directory.
    """
    embeddings = get_embeddings()

    # Determine ChromaDB connection mode
    chroma_host = settings.chroma.host
    if chroma_host and chroma_host not in ("localhost", "127.0.0.1"):
        # Client-server mode (Docker / cloud)
        client = chromadb.HttpClient(host=chroma_host, port=settings.chroma.port)
        vectorstore = Chroma(
            client=client,
            collection_name=settings.chroma.collection_name,
            embedding_function=embeddings,
        )
    else:
        # Local persistent directory
        persist_dir = str(Path(__file__).resolve().parents[2] / "chroma_data")
        vectorstore = Chroma(
            collection_name=settings.chroma.collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )

    # Check if collection already has data
    try:
        existing = vectorstore._collection.count()
        if existing > 0:
            logger.info("Policy store already populated with %d chunks.", existing)
            return vectorstore
    except Exception:
        pass

    # Load and index policy documents
    policy_path = settings.app.policy_pdf_path
    resolved = Path(policy_path)
    if not resolved.is_absolute():
        resolved = Path(__file__).resolve().parents[2] / policy_path

    if resolved.exists() and resolved.suffix == ".pdf":
        documents = _load_documents_from_pdf(str(resolved))
    else:
        # Fallback to .txt version
        txt_path = resolved.with_suffix(".txt")
        if txt_path.exists():
            documents = _load_documents_from_text(str(txt_path))
        else:
            logger.warning(
                "No policy document found at %s or %s. "
                "Using empty policy store.",
                resolved,
                txt_path,
            )
            return vectorstore

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    chunks = text_splitter.split_documents(documents)

    if chunks:
        vectorstore.add_documents(documents=chunks)
        logger.info("Indexed %d policy chunks into ChromaDB.", len(chunks))

    return vectorstore


def retrieve_relevant_policies(query: str, vectorstore: Chroma, k: int = 6) -> str:
    """Retrieve and deduplicate relevant policy sections.

    Args:
        query: The search query.
        vectorstore: The Chroma vector store.
        k: Number of results to retrieve.

    Returns:
        Concatenated relevant policy text.
    """
    docs = vectorstore.similarity_search(query, k=k)

    section_map: dict[str, str] = {}
    for doc in docs:
        text = doc.page_content.strip()
        match = re.match(r"^\d+\.\d+\s+[A-Za-z ].+", text)
        section = match.group(0) if match else "OTHER"

        if section not in section_map:
            section_map[section] = text
        else:
            if text not in section_map[section]:
                section_map[section] += "\n" + text

    return "\n\n".join(section_map.values())
