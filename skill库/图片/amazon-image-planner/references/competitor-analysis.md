# Competitor-Informed Image Planning

Use this optional workflow when the user provides ASINs, competitor listing screenshots, competitor image descriptions, review excerpts, keyword data, Sorftime/market exports, or asks to analyze competitors, bad-review pain points, selling-point gaps, purchase barriers, or image strategy before making Amazon images.

Do not include real ASIN examples from source articles or prior conversations in this skill. If an example ASIN is needed, use a clearly fake placeholder such as `B0EXAMPLE1`.

## Evidence Inputs

Accept any available evidence. Do not require all inputs.

- Own product facts: title, bullets, specs, package contents, reference images, brand positioning.
- Target ASIN or competitor ASIN list.
- Competitor listing gallery screenshots or image descriptions.
- Competitor title, bullets, A+ content, or review excerpts.
- Keyword list, search terms, reverse-lookup phrases, or ad terms.
- Category context, target buyer profile, or Sorftime/market exports.

## Sorftime MCP Research

When Sorftime MCP tools are available and the user asks to research an ASIN or competitor set, use them before image planning. Default `amzSite` / `site` to `US` unless the user specifies another Amazon marketplace.

Recommended sequence for a target ASIN:

1. Call `mcp__sorftime_server.product_detail` to identify the product, title, category clues, variants, image/listing evidence returned by the tool, and factual product constraints.
2. Call `mcp__sorftime_server.product_report` to gather product performance context, related keywords, competitor/similar ASINs, category signals, or any market summary fields returned by Sorftime.
3. Call `mcp__sorftime_server.product_customers_say` to capture summarized buyer sentiment and recurring praise/complaint themes.
4. Call `mcp__sorftime_server.product_reviews` with `reviewType: "Negative"` to mine 1-3 star pain points. Use up to the returned limit; summarize patterns instead of quoting long reviews.
5. Call `mcp__sorftime_server.product_variations` when variant, color, size, pack count, or child-ASIN differences may affect image strategy.
6. For important keywords surfaced by the user or Sorftime, call `mcp__sorftime_server.product_ranking_trend_by_keyword` to understand whether the product has exposure for that keyword and how search intent should influence imagery.
7. For competitor ASINs found in Sorftime output or supplied by the user, repeat the lightweight subset: `product_detail`, `product_report` when useful, `product_customers_say`, and `product_reviews` with `reviewType: "Negative"`.

If Sorftime does not return competitor ASINs, do not invent them. Ask the user for competitor ASINs, screenshots, or an export, then continue. Do not use non-Amazon tools such as Shopee keyword search for Amazon image planning unless the user explicitly asks for cross-platform inspiration.

## Fallback Without Live Data

If the user only gives an ASIN and no Sorftime MCP or other live data source is available, state that live ASIN data is needed and ask for exported competitor/review/keyword evidence, screenshots, or permission to use an available research tool. Do not fabricate review themes, rankings, sales, competitor ASINs, or competitor claims.

## Analysis Sequence

Before image planning, build a compact Chinese analysis grounded in the evidence source:

1. Product positioning: identify what the product is really selling beyond the literal object, such as decor effect, convenience, protection, gifting, staging value, compatibility, or problem relief.
2. Keyword intent: map important search phrases to the buyer's mental image and evaluation criteria.
3. Competitor expression: summarize what competitors already show in MAIN, lifestyle, detail, size, bundle, use-step, benefit, and A+ images.
4. Review pain points: extract recurring concerns from negative reviews, such as quality mismatch, size surprise, hard setup, missing parts, weak material, inaccurate color, unclear use, misleading expectation, or poor packaging.
5. Selling-point gaps: identify credible, under-expressed angles the user's product can own visually.
6. Image priorities: translate purchase barriers and gaps into image jobs, ordered by expected conversion impact.

## Mapping Pain Points To Image Jobs

Use this mapping as a starting point, then adapt to the product:

- Looks cheap / like cardboard / flimsy: create material, edge, texture, structure, and close-up proof images.
- Size is smaller/larger than expected: create a dedicated dimensions image plus real-scene scale reference.
- Buyer does not know where or how to use it: create multi-scenario images tied to keyword intent.
- Buyer misunderstands product type: create gentle expectation-setting copy that names the product accurately.
- Setup feels hard: create unfold/install/use-step images with 3-4 simple steps.
- Missing accessories or unclear bundle: create package contents image with truthful count and fair visual importance.
- Color/style fit is uncertain: create scenario images that show target decor, outfit, device, room, season, or use environment.
- Durability or protection is questioned: create evidence-led detail images, avoiding unsupported lab-test or certification claims.

## Competitor Safety Rules

Use competitor evidence only to understand the market. Do not copy competitor brand names, packaging, product design, exact image composition, proprietary copy, icons, badges, or layout. Avoid saying the product is better than named competitors unless the user provides defensible comparative proof and Amazon policy permits it.

Do not convert review complaints into claims the user's product cannot prove. Phrase image copy as factual product information, expectation setting, or supported benefits.

## Output Add-On

When this workflow is used, include this section before Product Parse unless the user requests JSON only:

```markdown
**Competitor & Review Insight Summary**
- Data Sources:
- Product Positioning:
- Keyword Intent:
- Competitor Image Patterns:
- Review Pain Points:
- Selling-Point Gaps:
- Image Priority:
```

Then reflect the insights inside each image plan:

- Name the buyer objection or keyword intent the slot addresses.
- Explain what visual evidence will resolve it.
- Keep on-image copy short, concrete, and US-English.
- Prefer one primary job per image; do not crowd every pain point into one layout.