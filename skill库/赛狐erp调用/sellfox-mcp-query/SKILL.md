---
name: sellfox-mcp-query
description: Query Sellfox-MCP for Amazon shop, sales, profit, order, MSKU, advertising, inventory, logistics, and reimbursement data with low-token, scope-safe workflows. Use when the user asks to call Sellfox-MCP or analyze Sellfox data.
---

# Sellfox-MCP 查询

Use the Sellfox-MCP gateway for read-only business queries. Never invent a tool ID, shop ID, currency, date range, or profit caliber. If the required contract is not already known, call `help`; if help does not include a complete schema, call `search`, then call `action` with the returned `contract_version`.

## Default account scope

For this account, default Amazon scope is only:

- US shop: `556961`
- Canada shop: `556962`

Exclude Mexico (`556963`) and Brazil (`556964`) unless the user explicitly changes the scope. Keep USD and CAD separate; never add different currencies.

## Efficient query rules

- Prefer shop-level profit reports for totals; use MSKU, SKU, or order reports only for diagnosis or detail.
- Pass the exact shop, marketplace, dates, currency, and `profit_caliber_type` (`settlement` or `shipment`).
- Use monthly aggregation for monthly totals. For detail, use exact MSKU/SKU/ASIN filters and small pages (`page_size` 1–3).
- The API returns a fixed wide record; do not print the raw response. Extract only requested fields, normally MSKU, sales units, sales, refunds, gross profit, and gross-profit rate.
- Check `status`, `coverage.complete`, pagination, and `warnings`. A successful first page is not a complete result.
- If an upstream transport/read error repeats, reduce the date range, shop scope, or page size. Do not treat partial data as a complete total.

## Interpretation

Label `grossProfit` as 毛利润, not net profit. Preserve the API's original values, including zero-sales rows with fees, negative-profit rows, and small rounding differences. Explain when dashboard totals differ from reports: dashboard scope, real-time refresh, shipment vs settlement caliber, currency conversion, advertising-cost source, or cost configuration may differ.

## Response style

Lead with the result. Use a compact table for parallel metrics. State date range, shops, currency, caliber, and completeness. If a field is unavailable or a page failed, say so instead of estimating.
