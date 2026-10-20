# Slot And Module Specs

## Listing Slots

Default listing image count: 7.

- `MAIN`: pure white Amazon main image.
- `PT01-PT06`: secondary listing images.

Support 7-12 listing images when requested. Continue slot naming as `PT07`, `PT08`, and so on.

Recommended gallery mix for a typical 7-image set:

- `MAIN`: white background product identification.
- `PT01`: strongest benefit or hero lifestyle/info image.
- `PT02`: detail/material/structure evidence.
- `PT03`: scale, dimensions, fit, or compatibility.
- `PT04`: package contents or what is included.
- `PT05`: use steps, installation, care, or problem-solution.
- `PT06`: text-free lifestyle scene, brand mood, or secondary benefit.

Adjust the mix to the product. Do not force irrelevant image types.

## A+ Content Types

When A+ is requested but the type is unspecified, ask the user to choose Regular A+ or Premium A+ before planning. Use Regular A+ (`standard-large`) only if the user explicitly wants a conservative fallback without choosing.

### Regular A+ (`standard-large`)

- `A+L01-A+L05`: Single Image modules, upload `970x600`.

### Standard A+ (`standard`)

- `A+S01`: Header Banner, upload `970x300`.
- `A+S02-A+S04`: Single Image modules, upload `970x600`.
- `A+S05-A+S08`: Highlight Tile modules, upload `220x220`; usually pair with external textTitle/textBody instead of drawing dense text inside the square.

### Premium A+ (`premium`)

Plan every Premium A+ slot as a paired desktop and mobile asset with the same message but independently composed layouts:

- `A+P01-D` through `A+P06-D`: desktop assets, upload `1464x600`.
- `A+P01-M` through `A+P06-M`: matching mobile assets, upload `600x450`.
- Support `A+P07-D` and `A+P07-M` only when the user requests a seventh Premium module.

Do not use `970x600` or `463x625` for Premium A+ in this workflow. Those dimensions belong to other A+ or brand-content contexts, not the paired Premium desktop/mobile deliverable defined here.

The mobile asset is not a separate A+ plan. It is the companion composition for the same `A+Pxx` slot. Preserve the same selling point, product truth, and copy intent while simplifying layout density for mobile.

## Generation Size Guidance

If the user needs generation sizes, use high-resolution canvases with the same aspect ratio as the final upload size, then resize proportionally. Avoid crop-based workflows for A+ images because cropping can remove product, copy, or safe-area content.

Recommended proportional generation targets:

- Square listing images: generate `2048x2048`, final upload may be resized square if needed.
- Regular A+ Single Image `970x600`: generate `1940x1200`, then resize proportionally to `970x600`.
- Premium A+ desktop `1464x600`: generate `2928x1200`, then resize proportionally to `1464x600`.
- Premium A+ mobile `600x450`: generate `1200x900`, then resize proportionally to `600x450`.

Do not derive the Premium mobile asset by automatically cropping the desktop banner. The desktop and mobile aspect ratios differ materially; compose each asset separately around the same message and Product Reference Lock.

If the exact high-resolution target is not supported by the image model, choose the nearest supported larger canvas with the same aspect ratio. Do not plan a composition that requires later cropping. Keep all important product, text, and callouts inside the final aspect-ratio safe area.

If the user explicitly asks for 4K, state the larger same-ratio target in the prompt. Do not promise exact Seller Central file-size compliance after generation; final compression under 2 MB may still be needed outside Codex.

## Mandatory Dimension Validation

After generation, inspect the saved file's actual pixel width and height; never infer dimensions from the prompt, filename, tool preview, or rounded display metadata.

- Validate aspect ratio by exact cross multiplication: `actualWidth * targetHeight == actualHeight * targetWidth`.
- A generator result that fails the target ratio is an intermediate asset only. Do not label or deliver it as the approved high-resolution source/master.
- First regenerate once with the exact target ratio, explicit safe-area margins, and a same-ratio high-resolution canvas request.
- If the generator still returns a near-match, correct it only when the composition has verified safe margins. Use the smallest symmetric crop or background padding needed to reach an exact same-ratio master; never stretch or non-proportionally resize the artwork.
- If correction would cut product, copy, callouts, or required safe-area content, regenerate or recompose instead of silently cropping.
- Create the upload file from the validated exact-ratio master by proportional resizing only.
- Re-open every final file and report its measured pixel dimensions. For A+ uploads, also check the final encoded file size against the applicable upload limit.

Examples:

- Regular A+: validate or normalize the master to exactly `1940x1200`, then resize proportionally to exactly `970x600`.
- Premium desktop: validate or normalize the master to exactly `2928x1200`, then resize proportionally to exactly `1464x600`.
- Premium mobile: validate or normalize the master to exactly `1200x900`, then resize proportionally to exactly `600x450`.

A raw result such as `1594x987` must not be called the source/master for any of these targets because it does not exactly match their required aspect ratios.
