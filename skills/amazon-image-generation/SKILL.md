---
name: amazon-image-generation
description: Amazon Listing and A+ Content image planning plus optional Codex-chat image generation workflow. Use when the user asks Codex to plan Amazon product listing images, A+ module images, ecommerce product image prompts, MAIN/PT01-PT06 galleries, A+L/A+S/A+P/A+M modules, Amazon-compliant image prompts, product-reference image consistency, competitor/ASIN/Sorftime/review-pain-point analysis for image selling points, or to directly generate ecommerce images inside the Codex conversation without a separate API key.
---

# Amazon Image Planner

## Workflow

Use this skill to turn Amazon product copy, bullet points, reference-image descriptions, competitor insights, review pain points, or brand notes into compliant image plans and English image-generation prompts. The workflow has three modes:

1. Planning mode: output structured plans and prompts only.
2. Competitor-informed planning mode: use supplied evidence or available Sorftime MCP data to analyze ASINs, competitor image patterns, keyword intent, review pain points, and selling-point gaps before image planning.
3. Direct generation mode: create the plans, then generate selected images in the Codex conversation with the available image generation tool.

First identify the requested deliverable:

- Listing image set: use `MAIN` plus `PT01` through `PT06` by default. Support 7-12 listing images if the user asks for more.
- A+ Content: choose the requested type. If the user asks for A+ but does not specify the type, ask whether to plan Regular A+ (`A+L01-A+L05`, 970x600 Single Image modules) or Premium A+ (`A+P`, including 1464x600 desktop and 600x450 mobile modules) before planning.
- Premium A+ asset pairing: plan each `A+Pxx` slot as two independently composed companion assets, `A+Pxx-D` at `1464x600` for desktop and `A+Pxx-M` at `600x450` for mobile. Do not use Regular A+ `970x600` or brand-content `463x625` dimensions for Premium A+ in this workflow.
- Competitor-informed plan: when the user provides ASINs, competitor screenshots/listing copy, review excerpts, keyword data, Sorftime exports, or asks for competitor analysis, pain-point mining, image selling points, purchase barriers, or market gaps, read `references/competitor-analysis.md` before planning.
- Direct generation: plan first, ask only if the requested batch is ambiguous or too large; otherwise generate the requested slots. For a full set, start with `MAIN` and `PT01` unless the user explicitly asks to generate every slot.

Read `references/amazon-rules.md` before planning or generating. Read `references/competitor-analysis.md` when competitor/ASIN/Sorftime/review/keyword evidence should shape image selling points. Read `references/reference-lock.md` whenever reference images are provided or product consistency matters. Read `references/module-specs.md` when working with A+ modules or upload/generation sizes. Read `references/output-contract.md` when producing structured output or direct-generation prompts.

## Planning Rules

Extract or infer conservatively:

- Product title, category, brand/model, color, material/finish, target audience, usage scene, package contents.
- Up to five core selling points.
- Search intent and buyer mental images when keyword evidence is supplied.
- Purchase barriers, review pain points, competitor image claims, and under-expressed market gaps when competitor evidence is supplied.
- Risky or forbidden elements from the user request.
- Product Reference Lock when product reference images are supplied: silhouette, color, material, logo/text placement, distinctive parts, openings, buttons, seams, dimensions, package contents, and anything that must not change.

Use reference images only as product evidence: appearance, shape, structure, color, materials, included accessories, packaging, and visible product text. Do not use reference images to impose unrelated style, palette, typography, props, scene, or mood unless the user explicitly asks. Use competitor materials only for market insight, buyer concern discovery, and layout category awareness; never copy competitor product design, branding, exact composition, claims, or text. When consistency matters, state the Product Reference Lock before image plans and repeat the lock inside every generation prompt.

Write `planMarkdown` in Simplified Chinese. Write final image prompts, negative prompts, and `seriesStyleGuide` in English. On-image copy should be US English, concise, mobile-readable, and never Chinese unless the product itself visibly contains that text.

For each slot, produce:

- Slot id and short Chinese label.
- Chinese planning notes covering goal, composition, product evidence, copy strategy, compliance risks, reference-image usage, and competitor/pain-point rationale when relevant.
- English prompt that fully specifies the finished image.
- English negative prompt.

## Direct Generation

When the user asks to generate images directly, do not stop at prompts. After planning:

1. Select the requested slot or slots.
2. Build the final English prompt using the slot prompt, Product Reference Lock, style guide if applicable, final output size, and negative prompt.
3. Generate one image per selected slot through the available image generation tool, using the user-provided product images as references when available.
4. Present each result with its slot name, purpose, prompt summary, and download/preview image.
5. For every saved deliverable, read the actual pixel dimensions from the file and validate them against the required slot or module size. Treat a generator-returned image with the wrong aspect ratio as an intermediate, not as an approved source/master. Follow the correction and validation rules in `references/module-specs.md` before delivery.
6. Keep rejected generations, raw tool outputs, and superseded corrections outside the user-facing deliverables directory. Follow the canonical-output rules in `references/output-contract.md`; do not leave duplicate `v1`/`v2` files in `outputs` unless the user explicitly requests version history or multiple approved variants.

For direct generation, keep batches controlled. Generate 1-2 images first when the user asks for a full set and has not approved a final visual direction. Continue with the remaining slots after the user accepts the direction.

## Output Defaults

For Listing plans, default to:

- `MAIN`: Amazon-compliant pure white main product image.
- `PT01-PT06`: a balanced mix of lifestyle, detail, scale/dimensions, package contents, use steps, and benefit/info images based on the product facts.

When competitor or review evidence is available, prioritize slots that answer buyer objections and keyword intent: credibility, material/quality proof, scale/fit, included contents, use clarity, scenario fit, expectation setting, and differentiation from crowded competitor claims.

For A+ plans, do not silently choose the A+ type when the user has not specified it. Ask whether to use Regular A+ or Premium A+ first. If the user explicitly asks to proceed without choosing, use Regular A+ as the conservative fallback:

- `A+L01-A+L05`: Single Image modules, upload `970x600`.

Avoid inventing unsupported product claims, certifications, awards, warranties, medical/health claims, review claims, pricing, discounts, marketplace badges, or brand assets.
