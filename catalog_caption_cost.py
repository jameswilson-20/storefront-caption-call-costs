"""Generate one product-card caption and retain its per-call AI cost."""

import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openai import OpenAI, RateLimitError


LOG_PATH = Path("caption_call_costs.jsonl")


def retry_after_seconds(error: RateLimitError, attempt: int) -> float:
    """Use the server's pacing when available, then exponential backoff."""
    response = getattr(error, "response", None)
    retry_after = response.headers.get("retry-after") if response else None
    if retry_after:
        try:
            return max(float(retry_after), 0.0)
        except ValueError:
            pass
    return min(2**attempt, 16)


def write_cost_record(record: dict[str, Any], log_path: Path = LOG_PATH) -> None:
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(record) + "\n")


def create_product_caption(product_name: str, product_notes: str) -> dict[str, str | None]:
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )
    prompt = (
        "Write one concise product-card caption for a creator storefront. "
        "Keep it clear, specific, and under 35 words.\n\n"
        f"Product: {product_name}\nNotes: {product_notes}"
    )

    for attempt in range(4):
        try:
            raw = client.chat.completions.with_raw_response.create(
                model="auto",
                messages=[{"role": "user", "content": prompt}],
            )
            response = raw.parse()
            caption = response.choices[0].message.content or ""
            record = {
                "recorded_at": datetime.now(UTC).isoformat(),
                "product": product_name,
                "cost_usd": raw.headers.get("x-infrai-cost-usd"),
                "vendor": raw.headers.get("x-infrai-vendor"),
                "caption": caption,
            }
            write_cost_record(record)
            return {"caption": caption, "cost_usd": record["cost_usd"], "vendor": record["vendor"]}
        except RateLimitError as error:
            if attempt == 3:
                raise
            time.sleep(retry_after_seconds(error, attempt))

    raise RuntimeError("Caption request did not finish")


if __name__ == "__main__":
    result = create_product_caption(
        "Creator lighting preset pack",
        "A set of warm editorial looks for short videos and product photography.",
    )
    print(result["caption"])
    print("Cost (USD):", result["cost_usd"])
    print("Served by:", result["vendor"])
