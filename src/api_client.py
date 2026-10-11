"""Small REST API client with validation and clear failure messages."""
import argparse
import json
from pathlib import Path
from typing import Any

import requests

DEFAULT_BASE_URL = "https://jsonplaceholder.typicode.com"


class ApiIntegrationError(RuntimeError):
    """Raised when an API call or response cannot be used."""


def fetch_post(post_id: int, base_url: str = DEFAULT_BASE_URL, timeout: float = 5.0) -> dict[str, Any]:
    """Fetch one post and validate the response shape."""
    if post_id < 1:
        raise ValueError("post_id must be a positive integer")

    url = f"{base_url.rstrip('/')}/posts/{post_id}"
    try:
        response = requests.get(url, timeout=timeout)
    except requests.Timeout as exc:
        raise ApiIntegrationError(f"Request timed out after {timeout} seconds") from exc
    except requests.RequestException as exc:
        raise ApiIntegrationError(f"Request failed: {exc.__class__.__name__}") from exc

    if not response.ok:
        raise ApiIntegrationError(f"API returned HTTP {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise ApiIntegrationError("API response was not valid JSON") from exc

    required = {"userId", "id", "title", "body"}
    if not isinstance(data, dict) or not required.issubset(data.keys()):
        raise ApiIntegrationError("API response is missing one or more required fields")

    if not isinstance(data["title"], str) or not isinstance(data["body"], str):
        raise ApiIntegrationError("API response fields 'title' and 'body' must be strings")

    return data


def make_report(post: dict[str, Any], elapsed_ms: float) -> dict[str, Any]:
    """Create a small, safe-to-share integration summary."""
    return {
        "integration_status": "success",
        "endpoint_resource": "posts",
        "record_id": post["id"],
        "required_fields_validated": True,
        "response_time_ms": round(max(elapsed_ms, 0), 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and validate a demo REST API post.")
    parser.add_argument("--post-id", type=int, default=1)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    import time
    started = time.perf_counter()
    try:
        post = fetch_post(args.post_id, base_url=args.base_url, timeout=args.timeout)
    except (ApiIntegrationError, ValueError) as exc:
        print(json.dumps({"integration_status": "failure", "error": str(exc)}, indent=2))
        return 1

    elapsed_ms = (time.perf_counter() - started) * 1000
    result = {
        "id": post["id"],
        "title": post["title"],
        "body": post["body"],
    }
    print(json.dumps(result, indent=2))

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(make_report(post, elapsed_ms), indent=2) + "\n", encoding="utf-8")
        print(f"\nIntegration report written to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
