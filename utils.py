import json
import os
from autogen_core.components.models import (
    ChatCompletionClient,
    ModelCapabilities,
)
from autogen_ext.models import OpenAIChatCompletionClient
from typing import Any, Dict

ENVIRON_KEY_CHAT_COMPLETION_PROVIDER = "CHAT_COMPLETION_PROVIDER"
ENVIRON_KEY_CHAT_COMPLETION_KWARGS_JSON = "CHAT_COMPLETION_KWARGS_JSON"

def create_completion_client_from_env(env: Dict[str, str] | None = None, **kwargs: Any) -> ChatCompletionClient:
    """
    Create a model client based on information provided in environment variables.
        env (Optional):     When provided, read from this dictionary rather than os.environ
        kwargs**:           ChatCompletionClient arguments to override (e.g., model)
    """
    if env is None:
        env = dict()
        env.update(os.environ)

    # Load the kwargs, and override with provided kwargs
    _kwargs = json.loads(env.get(ENVIRON_KEY_CHAT_COMPLETION_KWARGS_JSON, "{}"))
    _kwargs.update(kwargs)

    # If model capabilities were provided, deserialize them as well
    if "model_capabilities" in _kwargs:
        _kwargs["model_capabilities"] = ModelCapabilities(
            vision=_kwargs["model_capabilities"].get("vision"),
            function_calling=_kwargs["model_capabilities"].get("function_calling"),
            json_output=_kwargs["model_capabilities"].get("json_output"),
        )

    # Determine the provider
    _provider = env.get(ENVIRON_KEY_CHAT_COMPLETION_PROVIDER, "ollama").lower().strip()

    if  _provider == "ollama":
        # Add support for Ollama
        return OpenAIChatCompletionClient(
            model="llama3.2:latest",
            base_url="http://localhost:11434/v1",
            api_key="placeholder",
            model_capabilities={
                "vision": False,
                "function_calling": True,
                "json_output": True,
            },
        )
    else:
        raise ValueError(f"Unknown provider '{_provider}'")