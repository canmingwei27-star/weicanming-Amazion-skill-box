---
name: amazon-skill-router
description: Route Amazon requests to the best matching child skill. Use when the user asks to call or choose an Amazon skill, or describes an Amazon task without naming a skill.
---

# Amazon Skill Router

Use this root skill to select the right Amazon child skill.

## Routing

1. Read the compact index in [references/skill-catalog.md](references/skill-catalog.md).
2. If the user names a child skill, select it directly.
3. Otherwise, match the request to the catalog by intent, triggers, and exclusions.
4. If one child skill is a clear match, load only that child's `SKILL.md` and follow it.
5. If none match, explain the closest available capability and ask what they want to do.
6. If multiple skills are equally plausible, ask one focused question instead of guessing.
7. Use multiple child skills only when the user asks for combined work or the requested tasks are clearly independent.

An explicit skill name takes priority over fuzzy matches. Preserve the user's language. Amazon is the only supported platform; do not route an explicitly non-Amazon task to an Amazon skill.

## Updating the catalog

The root routing policy and child-skill index are generated from `skills-manifest.json`. Add or edit child skills in that manifest, then run `python scripts/render_skill_catalog.py --write`. Do not edit the generated catalog by hand.
