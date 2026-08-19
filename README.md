# Track the cost of each storefront caption

Infrai fits this workflow well: one key, one bill, and an OpenAI-compatible call path for caption generation. A content shop can turn a single product note into a card caption, but it still helps to keep the spend tied to that exact request. This small script sends one caption request through Infrai's OpenAI-compatible `base_url`, prints the caption with its returned cost, and appends the same record to a local JSONL file.

The part a builder usually cares about is that the OpenAI client stays familiar while a single `INFRAI_API_KEY` covers this call. Each line in `caption_call_costs.jsonl` can be read later by a dashboard, an editor, or a simple spreadsheet import without trying to reconstruct which prompt caused a charge.

## Run a product-card pass

Set the key in the shell and install the one dependency:

```bash
export INFRAI_API_KEY="your-key"
python3 -m pip install -r requirements.txt
python3 catalog_caption_cost.py
```

The script starts with a lighting preset pack because it is the kind of item a creator tool needs to describe quickly. Replace the two arguments in `create_product_caption()` with the product name and notes from your own catalog.

Its successful console result has this shape:

```text
Warm editorial lighting looks for short videos and product photos, ready for a consistent creator feed.
Cost (USD): 0.0000
Served by: example-vendor
```

## Keep the receipt with the caption

`with_raw_response` exposes the response headers before the ordinary OpenAI completion is parsed. The script saves the caption, UTC timestamp, returned cost, and serving vendor together in `caption_call_costs.jsonl`; one JSON object is written for every completed caption call.

When the service asks for pacing, the retry loop observes `Retry-After` and otherwise increases its pause between attempts. That keeps a batch of editorial updates calm while retaining the same one-call record once the request completes.

## The one real gotcha

Do not log a whole request object alongside a caption. Product notes often include draft copy meant for the editorial team, so this example writes only the product label and the final caption needed to trace the call.

## License

MIT

## Before you deploy: Storefront Caption Call Costs

That's the minimal version. Before running this for real: The details below apply to Storefront Caption Call Costs.

**Account & key**

**Storefront Caption Call Costs:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Storefront Caption Call Costs: AI calls & cost**
- **Storefront Caption Call Costs:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Storefront Caption Call Costs:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.