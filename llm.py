import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()


def _create_llm() -> LLM:
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    if not all([azure_api_key, azure_endpoint, azure_deployment]):
        raise ValueError(
            "Missing Azure OpenAI configuration.\n"
            "Required env vars:\n"
            "- AZURE_OPENAI_API_KEY\n"
            "- AZURE_OPENAI_ENDPOINT\n"
            "- AZURE_OPENAI_DEPLOYMENT_NAME\n"
            "Optional:\n"
            "- AZURE_OPENAI_API_VERSION"
        )

    return LLM(
        model=azure_deployment,
        provider="azure_openai",
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=azure_api_version,
        temperature=0.7,
        extra_body={"prompt_cache_key": "investment-strategy-cache"},
    )
