# Wildlife character artwork

The collection uses individual illustrations for 98 birds and 24 bats. The jay
and tawny owl previews approved by the owner are the style references. Their
original WebP previews remain alongside the collection assets.

Generated with the built-in image generation tool, one image per species.
The brief combines the catalogue's scientific name and original field note
with the following direction:

> One original creature-collecting game portrait. Match the approved jay and
> owl's Pokémon/Pidgeotto-inspired crisp outlines, angular tufts, confident
> expressive poses and layered cel shading. Retain the species' real plumage
> or fur and distinguishing features. Full body, every exposed wingtip, ear,
> foot and tail inside the frame, with transparent margins. One animal on a
> genuinely transparent background. No scenery, gradient, glow, cast shadow,
> text, border or logo.

Bat prompts additionally specify mammalian faces, fur, finger-supported wing
membranes and each species' ear, noseleaf, muzzle and colour characteristics.
All reusable and species-specific prompts are kept in
[artwork-prompts.json](artwork-prompts.json).

## Poses

Preserve the current pose, facing direction, wing and foot positions, and tail
angle when revising style. Naturally tucked feet and occluded wings are fine.
Keep two wings, two legs and a natural neck position. Wings fold naturally at
rest or move plausibly together in flight; avoid a single wing raised in front
of the body as a presentation gesture.

Use existing species as pose references only: White-tailed Eagle (#065) follows
Honey-buzzard (#068), Black-headed Gull (#053) follows Barn Swallow (#038),
Common Wood Pigeon (#018) follows Stock Dove (#064), and Long-eared Owl (#046)
follows Tawny Owl (#044). Retain each target's own anatomy and distinguishing
features. Other bird and bat portraits keep their current poses.

## Sizing

Frame both bird and bat portraits on the same 1200 × 1200 transparent canvas.
Use the birds' visual scale for both collections: target 24% visible silhouette
area, capped at 1104 pixels in either direction for long wings, legs or tails.
Centre each silhouette and retain transparent margins. Run
`python3 scripts/normalize_artwork_framing.py` after accepting new artwork;
it skips assets already using this policy. This framing adjustment must not
change anatomy, expression or pose. The two approved previews retain their
original resolution.

## Files and review

Final files are local transparent WebP assets, up to 1200 pixels on the longest
edge, named `bird-NNN-pokemon.webp` or `bat-NNN-pokemon.webp` in
`chirpecho/web/static/species/`. Each entry in
`chirpecho/web/static/species/artwork-manifest.json` records its source generation
filename, dimensions and final file checksum.

Run `python3 scripts/build_artwork_gallery.py` to rebuild contact sheets for review.
The bilingual live gallery is served at `/artwork`; the legacy
`/static/artwork-preview.html` bookmark redirects there through the application. These are stylised game illustrations, not scientific identification
drawings. Undiscovered cards use the same WebP artwork with a solid silhouette
filter; the artwork gallery is an explicit preview of the entire set.
