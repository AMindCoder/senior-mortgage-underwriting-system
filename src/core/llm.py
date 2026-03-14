from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.core.config import settings


def get_llm() -> ChatOpenAI:
    """Return a configured ChatOpenAI instance."""
    return ChatOpenAI(
        model=settings.openai.model,
        temperature=settings.openai.temperature,
        api_key=settings.openai.api_key,
        base_url=settings.openai.api_base,
    )


def get_embeddings() -> OpenAIEmbeddings:
    """Return a configured OpenAIEmbeddings instance."""
    return OpenAIEmbeddings(
        model=settings.openai.embedding_model,
        api_key=settings.openai.api_key,
        base_url=settings.openai.api_base,
    )
