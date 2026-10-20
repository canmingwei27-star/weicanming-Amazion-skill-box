# Output Contract

Use this structure unless the user asks for a different format.

## Planning Output

When competitor, ASIN, keyword, or review evidence is used, add this section before Product Parse:

```markdown
**Competitor & Review Insight Summary**
- Product Positioning:
- Keyword Intent:
- Competitor Image Patterns:
- Review Pain Points:
- Selling-Point Gaps:
- Image Priority:
```

For Listing:

```markdown
**Product Parse**
- Title:
- Category:
- Brand/Model:
- Color/Material:
- Audience:
- Scene:
- Package Includes:
- Selling Points:

**Product Reference Lock**
List immutable product details from own-product references and user facts. Mark unknown details as unknown; do not invent them.

**Series Style Guide**
English neutral guide for product continuity, factual consistency, copy hierarchy, and set coherence. Do not lock palette, typography, background mood, or decorative style unless requested.

**Image Plans**
### MAIN - [Chinese label]
中文策划说明...
Prompt:
```text
English image prompt...
```
Negative:
```text
English negative prompt...
```

### PT01 - [Chinese label]
...
```

For A+:

```markdown
**Product Parse**
...

**A+ Type**
Regular A+ / Standard A+ / Premium A+ (paired desktop and mobile assets)

**Series Style Guide**
...

**A+ Module Plans**
### A+L01 - Single Image - upload 970x600
中文策划说明...
External Text:
- Title:
- Body:
Prompt:
```text
English image prompt...
```
Negative:
```text
English negative prompt...
```
```

For Premium A+, repeat this paired block for every `A+Pxx` slot:

```markdown
### A+P01-D - Desktop - upload 1464x600
Desktop composition notes, prompt, and negative prompt...

### A+P01-M - Mobile Companion - upload 600x450
Mobile composition notes, prompt, and negative prompt for the same message. Compose independently; do not auto-crop the desktop banner.
```

## Prompt Construction

Final prompt for direct generation should combine:

1. Slot prompt.
2. Product Reference Lock when references exist or consistency matters.
3. Optional competitor/review insight distilled into the slot's visual job, without naming or copying competitors.
4. Optional selected visual style if the user requested one.
5. Series style guide for secondary Listing and A+ images. Do not apply a style guide to `MAIN` unless the user explicitly asks and it remains Amazon-main-image compliant.
6. Layout density guidance if useful:
   - Rich: polished, information-rich Amazon layout, mobile-readable US-English copy, clear hierarchy.
   - Minimal: refined minimal layout with one or two dominant messages and generous spacing.
7. Final output resolution.
8. Negative prompt, including reference-mismatch negatives.

For `MAIN`, keep the final prompt white-background and text-free. Do not attach lifestyle style language.

## Direct Generation Output

When generating images in Codex conversation:

- Generate one image per requested slot.
- Label each image with slot id and purpose.
- Include a short prompt summary, not the entire prompt unless requested.
- Mention upload suggestion for A+ modules.
- If generating a full set, generate first-pass images in small batches and ask the user to approve style continuity before continuing.
- Keep generator originals, rejected images, temporary crops, and superseded corrections in a work/intermediate location, not in the user-facing deliverables directory.
- By default, deliver one canonical approved file per slot and required output size. For A+ modules that need both a master and an upload file, deliver exactly one canonical master and one canonical upload file per slot.
- Use stable filenames without revision suffixes for the final approved set, for example `A+L01-1940x1200.png` and `A+L01-970x600.jpg`.
- Do not leave visually duplicate `v1`, `v2`, `source`, or raw-generator files beside the final deliverables unless the user explicitly requests version history, alternatives, or multiple approved variants.
- When a QA correction replaces an unapproved file, move the rejected file to the work/intermediate location and replace the canonical deliverable. Do not create another user-facing version solely to preserve an error.
- If the user explicitly asks to preserve an existing approved asset while creating a new alternative, use versioned filenames and label the variants clearly.

## JSON Option

If the user requests JSON, return:

```json
{
  "competitorInsightSummary": {
    "productPositioning": "",
    "keywordIntent": [],
    "competitorImagePatterns": [],
    "reviewPainPoints": [],
    "sellingPointGaps": [],
    "imagePriority": []
  },
  "product": {
    "title": "",
    "category": "",
    "brand": "",
    "color": "",
    "material": "",
    "audience": "",
    "scene": "",
    "packageIncludes": ""
  },
  "sellingPoints": [],
  "productReferenceLock": "",
  "seriesStyleGuide": "",
  "imagePlans": [
    {
      "slot": "MAIN",
      "label": "",
      "planMarkdown": "",
      "prompt": "",
      "negativePrompt": ""
    }
  ],
  "aPlusPlans": [
    {
      "slot": "A+L01",
      "label": "Single Image",
      "moduleType": "single-image",
      "uploadSize": "970x600",
      "generationSize": "2048-style wide",
      "planMarkdown": "",
      "textTitle": "",
      "textBody": "",
      "prompt": "",
      "negativePrompt": ""
    }
  ]
}
```