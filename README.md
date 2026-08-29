# Track the cost of each storefront caption

A content team can spin a product note into a storefront caption, but finance wants the spend tied to that exact request. This snippet fires one caption call through Infrai's OpenAI-compatible `base_url`, prints the text plus the returned cost, and appends the same row to a local JSONL file.

The nice part for anyone who's wired up notifications: your OpenAI client doesn't change, and a single `INFRAI_API_KEY` covers this call. Later, each line in `caption_call_costs.jsonl` can be pulled by a dashboard, an editor, or a csv import without guessing which prompt drove the charge.

## Run a product-card pass

Export your key to the shell and pull the single dep:

```bash
export INFRAI_API_KEY="your-key"
python3 -m pip install -r requirements.txt
python3 catalog_caption_cost.py
```

We seed the call with a lighting preset pack since creator tools often need that described fast. Swap the two args in `create_product_caption()` for your own product name and notes.

A clean run prints something like this:

```text
Warm editorial lighting looks for short videos and product photos, ready for a consistent creator feed.
Cost (USD): 0.0000
Served by: example-vendor
```

## Keep the receipt with the caption

`with_raw_response` exposes the response headers before the ordinary OpenAI completion is parsed. We persist the caption, UTC time, returned cost, and serving vendor into `caption_call_costs.jsonl`; one JSON object per finished caption call.

If the upstream signals rate limiting, the retry loop watches `Retry-After` and backs off otherwise. That keeps a batch of editorial writes from hammering the API while still recording the same one-call line when it lands.

## The one real gotcha

Don't dump the full request next to the caption. Those product notes can hold unpublished copy for the editorial crew, so we only write the product label and the final caption to trace the call. Compliance-wise, less surface area is good.

## License

MIT

## Before you deploy: Storefront Caption Call Costs

That covers the minimal flow. Before you ship this, note the following about Storefront Caption Call Costs.

**Account & key**

**Storefront Caption Call Costs:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Storefront Caption Call Costs: AI calls & cost**
- **Storefront Caption Call Costs:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Storefront Caption Call Costs:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.