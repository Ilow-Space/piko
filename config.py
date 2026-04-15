import os
from pydantic import BaseModel


class Config(BaseModel):
    # Ollama's OpenAI-compatible endpoint
    VLLM_API_BASE: str = "http://localhost:11434/v1"

    # Using your existing Qwen model for reasoning and coding
    VLLM_MODEL_NAME: str = "qwen2.5-coder:7b"

    LANCEDB_URI: str = "./memory/.lancedb"

    # Using your existing Nomic model for the router
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"

    ROUTER_THRESHOLD: float = 0.85
    DIRECTIVES_DIR: str = "./compiled_directives"


settings = Config()
