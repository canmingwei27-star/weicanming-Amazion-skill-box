# Product Reference Lock

Use this reference-lock workflow whenever the user provides product images, asks for consistency, or says the generated image does not match the reference.

## Reference Image Roles

Classify every provided image before planning:

- Own product reference: authoritative for product appearance. Use these for shape, color, materials, logo/text placement, package contents, and distinctive details.
- Own packaging or accessory reference: authoritative for included items, packaging, bundle quantity, labels, and kit layout.
- Own lifestyle reference: useful for real use context, scale, and scene evidence, but not a reason to change the product design.
- Competitor reference: non-authoritative. Use only for market layout inspiration, buyer concern discovery, or information density. Never copy competitor product design, branding, exact composition, text, claims, or packaging.
- Style reference: non-product aesthetic reference. Use only for palette, lighting, material finish, typography feel, and polish. Never copy product shape, props, layout, count, or text from it.

If image roles are unclear, infer conservatively and ask the user to identify which images are their own product before generating final images.

## Build The Lock

Before planning images, write a concise Product Reference Lock with these fields when visible or supplied:

- Product identity: exact product type, variant, model, brand.
- Silhouette and proportions: overall shape, aspect, size impression, curves, corners, thickness, handle/strap/neckline/etc.
- Color and finish: exact visible colors, transparency, gloss/matte/metal/wood/fabric texture.
- Materials and construction: seams, joints, ports, buttons, panels, surface patterns, stitching, edges, hardware.
- Distinctive marks: logos, printed words, icons, labels, embossing, engravings, and their placement.
- Count and bundle: number of items, included accessories, packaging, spare parts, cards, cables, lids, bags.
- Packaging facts: box/bag/tube shape, visible package color, label placement, included package only if meant to be shown.
- Must-not-change list: wrong color, extra parts, missing parts, altered logo, invented packaging, wrong count, wrong material, distorted dimensions.

If a fact is not visible or supplied, mark it as unknown instead of inventing it.

## Prompt Lock Block

Include a block like this in every direct-generation prompt when references exist:

```text
Product Reference Lock:
Use the uploaded own-product reference images as the primary source of truth for the product. Preserve the exact product silhouette, proportions, color, material finish, visible logo/text placement, distinctive structural details, included accessories, and bundle quantity. Do not redesign the product, change color, add or remove parts, invent logos, invent packaging, alter printed text, or borrow product details from competitor/style references. If a visual detail is unclear, keep it neutral rather than inventing it.
```

Then add product-specific locked details as bullets.

## Negative Prompt Additions

Append concrete mismatch terms to the negative prompt:

```text
wrong product shape, redesigned product, changed color, extra parts, missing parts, incorrect accessory count, invented logo, altered logo placement, invented printed text, wrong material, wrong texture, competitor product design, copied competitor branding, copied competitor packaging, inaccurate packaging, distorted proportions
```

Add product-specific negatives, for example: `extra handle`, `missing lid`, `wrong button layout`, `different nozzle`, `incorrect strap`, `wrong fabric texture`.

## Generation Strategy

For best consistency:

1. Generate or fix `MAIN` first using only own-product references, no style reference, no lifestyle props, and no text overlays.
2. Use the approved `MAIN` result as an additional visual anchor for later secondary images when possible.
3. For secondary Listing and A+ images, preserve the same locked product while changing only scene, layout, camera angle, callouts, or module composition.
4. If a generated image drifts, rewrite the next prompt as a correction: name the exact mismatch and add it to both the lock and negative prompt.
5. Do not ask the image model to imitate a competitor image. Ask it to create a new layout while preserving the user's own product reference.

## Consistency QA

After each generated image, check:

- Does the product silhouette match the own reference?
- Are color, material, texture, logo/text, and distinctive parts preserved?
- Are accessory count and package contents truthful?
- Did the image borrow any competitor branding, product shape, or packaging?
- Did A+ or lifestyle styling change the actual product design?

If any answer fails, tell the user the mismatch and regenerate with a stronger lock.