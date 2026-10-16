---
name: amazon-skill-router
description: Route exact or fuzzy Amazon requests to the correct child skill by reading the skill catalog. Use for requests such as 调用skill, 调用亚马逊skill, 选择亚马逊技能, or when the user describes a task without naming a skill. Amazon is the only supported platform.
---

# Amazon Skill Router

This is the entry-point skill for the skill box. Use it to decide which Amazon child skill should handle the user's request.

## Platform boundary

This skill box supports Amazon only. If the user does not name a platform, interpret the request as Amazon. If the user explicitly names another platform, do not route the request to an Amazon child skill; state that only Amazon is supported.

## Routing workflow

1. Read [references/skill-catalog.md](references/skill-catalog.md).
2. Match the user's intent to the child skill whose capability best fits the request. Match meaning, not exact wording.
3. If the user explicitly names a child skill, use that child skill.
4. If the user uses a fuzzy request such as “调用评论分析 skill”, route it to `amazon-review-analysis`.
5. If no child skill matches, explain which Amazon capability is currently available and ask for the missing input or a new skill request.

## Fuzzy invocation rules

Treat these as calls to the router:

- `调用 skill`
- `调用亚马逊 skill`
- `调用亚马逊技能`
- `选择合适的 skill`
- `帮我找需要调用的 skill`

Treat these as calls to the Amazon review-analysis child skill:

- `评论分析`
- `调用评论分析 skill`
- `亚马逊评论分析`
- `买家评论分析`
- `review analysis`

The user does not need to provide an exact `$skill-name`. Preserve the user's requested language and follow the selected child skill's output rules.

## Catalog maintenance

When a new child skill is added, add it to `skills-manifest.json`, add its routing entry to [references/skill-catalog.md](references/skill-catalog.md), and append its description to the repository README. Do not remove or rewrite existing entries without explicit authorization.

