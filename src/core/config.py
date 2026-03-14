import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env from project root
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)


class OpenAISettings(BaseSettings):
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    api_base: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


class PostgresSettings(BaseSettings):
    user: str = os.getenv("POSTGRES_USER", "underwriting")
    password: str = os.getenv("POSTGRES_PASSWORD", "underwriting_secret")
    db: str = os.getenv("POSTGRES_DB", "mortgage_underwriting")
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class ChromaSettings(BaseSettings):
    host: str = os.getenv("CHROMA_HOST", "localhost")
    port: int = int(os.getenv("CHROMA_PORT", "8000"))
    collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "underwriting_policies")


class AppSettings(BaseSettings):
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8501"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    environment: str = os.getenv("ENVIRONMENT", "development")
    policy_pdf_path: str = os.getenv("POLICY_PDF_PATH", "data/underwriting_policies.pdf")


class Settings:
    openai = OpenAISettings()
    postgres = PostgresSettings()
    chroma = ChromaSettings()
    app = AppSettings()


settings = Settings()
