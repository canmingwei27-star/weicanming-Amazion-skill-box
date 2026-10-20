---
name: amazon-review-analysis
description: Analyze Amazon buyer reviews or create a reusable review-analysis prompt, grouping product strengths and weaknesses by frequency. Automatically apply to exact or fuzzy requests such as 评论分析, 调用评论分析 skill, 亚马逊评论分析, 买家评论分析, or review analysis. Amazon is the only supported platform.
---

# Amazon Review Analysis

Use this skill when the user provides Amazon buyer reviews for analysis, asks for a reusable AI prompt to analyze reviews, or requests product-development insights grounded in review feedback. Follow the user's requested language; otherwise, report in Chinese and preserve useful customer wording in English when appropriate.

## Invocation and platform scope

Treat the following as calls to this skill, even when the user does not use the exact skill name:

- `调用评论分析 skill`
- `评论分析`
- `亚马逊评论分析`
- `买家评论分析`
- `review analysis` or `Amazon review analysis`

If the user asks for “评论分析” without naming a platform, interpret it as Amazon because Amazon is the only platform supported by this skill and this skill box. Do not require the user to say `$amazon-review-analysis`.

If the user explicitly names another platform, do not silently analyze it with this skill. State that the current skill supports Amazon only and ask the user to provide Amazon review data or a separately supported platform skill.

## Input format

For Excel review files, recognize this filename convention:

`{ASIN}-US-Reviews-{YYYYMMDD}.xlsx`

Example: `B0DB88Q37D-US-Reviews-20261016.xlsx`. Read the filename date as the review data/export date, not as the date of each individual review. Use the filename to identify the expected ASIN and marketplace, while using the `ASIN` column as the row-level source of truth. If the filename ASIN and table rows conflict, flag the mismatch and keep counts separated by the ASIN column; do not silently relabel rows. If the date or another filename component is missing or malformed, report it as unavailable rather than guessing.

The default table has three columns:

| ASIN | 标题 | 内容 |
| --- | --- | --- |
| B0... | Review title | Review text |

Interpret `标题` as the buyer review title and `内容` as the review body. Treat each data row as one review. Group and report results separately for each ASIN. When the user supplies more than one ASIN, do not combine their counts; compare products only when asked. If the table uses equivalent column names, map them by meaning. If the ASIN or review text is missing, state the limitation and analyze what can be reliably identified.

## Choose the deliverable

- If review text or a review file is provided, analyze the available data directly.
- If the user asks for a prompt/template and provides no review data, create a copy-ready prompt with clear input fields and an output schema. Do not invent review findings.
- If both are provided, analyze the reviews; include a reusable prompt only if requested.

## Analyze reviews

1. Establish the dataset for each ASIN: count data rows, identify available fields, and note missing or suspected duplicate records. If exact duplicates appear, flag them and explain whether they were included; do not silently remove rows when there is no review ID to confirm duplication.
2. Exclude blank or unusable review bodies from that ASIN's analyzable denominator, and report how many were excluded and why. Keep short but meaningful reviews. Titles may add context but should not be treated as a separate review.
3. Group semantically equivalent feedback into a single theme. Count a theme at most once per review row, even if the reviewer repeats it. One row may count toward multiple distinct themes.
4. Categorize themes under relevant dimensions, such as quality/durability, functionality/performance, materials/build, size/fit/compatibility, setup/use, design, packaging/accessories, value, and delivery/seller support. Add dimensions supported by the reviews.
5. Separate product feedback from shipping, seller, and customer-service feedback. Distinguish observed defects from subjective preferences, isolated reports from recurring patterns, and evidence from interpretation.
6. For each theme, report the number of distinct review rows mentioning it and its share of that ASIN's analyzable reviews: `mention rate = rows mentioning theme / analyzable review rows`. A review may contribute to multiple themes, so theme percentages do not need to add to 100%.
7. Assign frequency by mention rate: high at 20% or above; medium at 5% to below 20%; low below 5%. Always show the raw count and percentage. For small samples, explain that one or two rows can materially change the rate and avoid broad claims.
8. Assess frequency separately from severity. Rate severity as high, medium, or low based on the described effect on function, safety, usability, or return likelihood, and explain the evidence. Do not infer a safety hazard unless the reviews support it.
9. Use brief paraphrased examples when helpful. Never label a paraphrase as a direct quote. Preserve original wording for quoted excerpts and omit reviewer personal information.
10. Ground recommendations in the supplied reviews. Mark competitor comparisons, buyer demographics, market claims, or causes that the reviews cannot establish as unknown or requiring more evidence.

## Report format

For direct analysis, provide results separately by ASIN:

1. **总体结论** — number of supplied and analyzable reviews, overall pattern, leading strengths, main weakness, and data limitations.
2. **优点分析** — table with frequency, product dimension/theme, review-row count, mention rate, evidence summary, and product or listing implication.
3. **缺点分析** — table with frequency, product dimension/theme, review-row count, mention rate, severity, evidence summary, and grounded improvement suggestion.
4. **优先改进项** — rank actionable issues using frequency and severity together; do not describe a rare report as common.
5. **产品开发与运营建议** — distinguish necessary fixes, optional enhancements, and evidence-backed selling points. Keep product feedback separate from delivery or seller-service feedback.
6. **分析限制** — note small samples, missing rating/date/variant fields, possible duplicate rows, and conclusions the supplied data cannot support.

If there is little or no evidence for a requested dimension, say so instead of filling it with assumptions. When star ratings are absent, do not infer rating distributions; sentiment can only be described from the review text.

## Create a reusable prompt

When asked for a copy-ready prompt, make it usable with a pasted table or uploaded file, using the default columns `ASIN | 标题 | 内容` and defining title as review title and content as review body. Instruct the downstream AI to:

- analyze each ASIN separately and keep its denominator specific to that ASIN;
- treat each data row as one review and count each theme at most once per row;
- merge equivalent feedback and report row counts, denominator, and mention rates;
- apply the high/medium/low frequency bands above and caveat small samples;
- separate strengths, weaknesses, and non-product issues;
- distinguish mention frequency from severity;
- ground findings and recommendations in the supplied reviews;
- return an executive summary, categorized strengths and weaknesses, priority improvements, and product-development opportunities.

Keep the prompt easy to copy and edit. Do not hard-code unsupported product claims or instruct the model to scrape Amazon or access reviews the user has not supplied.

