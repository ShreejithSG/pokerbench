#!/usr/bin/env python3
"""
Check API key against OpenAI and LiteLLM proxy endpoints.
Loads .env from project root. Usage:

  python scripts/check_api.py

  # Or set env vars:
  export LITELLM_API_KEY=sk-your-key
  export LITELLM_BASE_URL=https://your-proxy.example.com
  python scripts/check_api.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
import sys

API_KEY = os.environ.get("LITELLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
BASE_URL = os.environ.get("LITELLM_BASE_URL")


def try_proxy(base_url: str, use_x_header: bool = False) -> tuple[bool | None, str]:
    """Try key against a LiteLLM proxy. Some proxies use x-litellm-api-key header."""
    if not API_KEY:
        return None, "No API key set"
    url = base_url.rstrip("/") + "/v1" if not base_url.endswith("/v1") else base_url.rstrip("/")
    try:
        from openai import OpenAI
        kwargs = {"base_url": url}
        kwargs["api_key"] = API_KEY
        if use_x_header:
            kwargs["default_headers"] = {"x-litellm-api-key": API_KEY}
        client = OpenAI(**kwargs)
        client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say ok"}],
            max_tokens=5,
        )
        return True, f"Proxy {base_url}: OK"
    except Exception as e:
        return False, f"Proxy {base_url}: {e}"


def try_openai_default():
    """Try key as standard OpenAI API key (no proxy)."""
    if not API_KEY:
        return None, "No API key set (LITELLM_API_KEY or OPENAI_API_KEY)"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say ok"}],
            max_tokens=5,
        )
        return True, f"OpenAI default: OK (model: {resp.model})"
    except Exception as e:
        return False, f"OpenAI default: {e}"


def main():
    print("Checking API key against endpoints...\n")
    key_preview = f"{API_KEY[:20]}...{API_KEY[-4:]}" if API_KEY else "NOT SET"
    print(f"Key: {key_preview}")
    if BASE_URL:
        print(f"Base URL: {BASE_URL}\n")
    else:
        print()

    # 1. If LITELLM_BASE_URL is set, try that proxy first (Bearer then x-litellm-api-key)
    if BASE_URL:
        ok, msg = try_proxy(BASE_URL, use_x_header=False)
        if ok:
            print(f"  [OK] {msg} (Authorization: Bearer)")
            print(f"\n  Use: base_url={BASE_URL} in your config")
            return 0
        print(f"  [FAIL] {msg}")
        ok, msg = try_proxy(BASE_URL, use_x_header=True)
        if ok:
            print(f"  [OK] {msg} (x-litellm-api-key header)")
            print(f"\n  Use: base_url={BASE_URL} with x-litellm-api-key header")
            return 0
        print(f"  [FAIL] {msg}")
        return 1

    # 2. Try OpenAI default
    ok1, msg1 = try_openai_default()
    if ok1 is True:
        print(f"  [OK] {msg1}")
        print("\n  Use: llm keys set openai  (paste the key)")
        return 0
    elif ok1 is False:
        print(f"  [FAIL] {msg1}")
    else:
        print(f"  [SKIP] {msg1}")

    # 3. Try local proxy
    ok2, msg2 = try_proxy("http://localhost:4000", use_x_header=False)
    if ok2 is True:
        print(f"  [OK] {msg2}")
        print("\n  Use: base_url=http://localhost:4000 in extra-openai-models.yaml")
        return 0
    elif ok2 is False:
        print(f"  [FAIL] {msg2}")
    else:
        print(f"  [SKIP] {msg2}")

    print("\n  Next steps:")
    print("  1. Set LITELLM_BASE_URL if you have a proxy URL (from Swagger/docs)")
    print("  2. Run local proxy: litellm --model gpt-4o --port 4000")
    print("  3. Use RandomPlayer: python run.py  (no API needed, omit --models)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
