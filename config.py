import os
from dotenv import load_dotenv
load_dotenv()


class PineconeConfig:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "asia-southeast1-gcp")
    PINECONE_NAME = os.getenv("PINECONE_NAME", "futurebot")
    PINECONE_NAMESPACES = ["talmud"]
    EMBEDDING_PACKAGE = os.getenv("EMBEDDING_PACKAGE", "openai")
    EMBEDDING_ENGINE = os.getenv("EMBEDDING_ENGINE", "text-embedding-ada-002")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    NUM_QUERY_RESPONSE = int(os.getenv("NUM_QUERY_RESPONSE", "1"))
    PINECONE_UPSERT_NAMESPACE = os.getenv("PINECONE_UPSERT_NAMESPACE", "talmud")


class OpenAIConfig:
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", None)
    MODEL_ENGINE = os.getenv("OPENAI_MODEL_ENGINE", "gpt-3.5-turbo")
    EMBEDDING_ENGINE = os.getenv("EMBEDDING_ENGINE", "text-embedding-ada-002")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    MAX_RETRY = int(os.getenv("MAX_RETRY", "5"))


class AI21Config:
    AI21_API_KEY = os.getenv("AI21_API_KEY")
    MODEL_ENGINE = os.getenv("AI21_MODEL_ENGINE", "j2-jumbo-instruct")


class AppConfig:
    # Flask specific varibles
    FLASK_SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "something")
    PORT=os.getenv("PORT", "8080")

    # Export Data Location
    BUCKET_NAME = os.getenv("BUCKET_NAME", "midrash-public")

    # Openai Streaming
    STREAM=os.getenv("STREAM", "True") == "True"

    # Google specific variables
    GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET", None)

    # Password
    HASH=os.getenv("HASH", "failed-to-find")

    # Test namespace variables
    TEST_NAMESPACE=os.getenv("TEST_NAMESPACE", "test")
    STAGE=os.getenv("STAGE", "dev")
