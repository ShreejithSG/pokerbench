"""API configuration for OpenAI and LiteLLM proxy."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class APIConfig:
    """API credentials and base URL from environment."""

    api_key: str | None
    base_url: str | None
    use_x_header: bool = False

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def openai_kwargs(self) -> dict:
        """Kwargs for OpenAI client (proxy or direct)."""
        if not self.api_key:
            return {}
        kwargs: dict = {"api_key": self.api_key}
        if self.base_url:
            url = self.base_url.rstrip("/")
            if not url.endswith("/v1"):
                url = f"{url}/v1"
            kwargs["base_url"] = url
            if self.use_x_header:
                kwargs["default_headers"] = {"x-litellm-api-key": self.api_key}
        return kwargs


def load_api_config(env_path: Path | None = None) -> APIConfig:
    """
    Load API config from environment.
    Prefers LITELLM_* for proxy, falls back to OPENAI_API_KEY for direct.
    """
    if env_path and env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)

    api_key = os.environ.get("LITELLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("LITELLM_BASE_URL")
    use_x_header = os.environ.get("LITELLM_USE_X_HEADER", "").lower() in ("1", "true", "yes")

    return APIConfig(api_key=api_key, base_url=base_url, use_x_header=use_x_header)
