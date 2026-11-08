# Wildlife character artwork

The collection uses individual illustrations for 71 birds and 24 bats. The jay
and tawny owl previews approved by the owner are the style references. Their
original WebP previews remain alongside the collection assets.

Generated with the built-in image generation tool, one image per species.
The brief combines the catalogue's scientific name and original field note
with the following direction:

> One original creature-collecting game portrait. Match the approved jay and
> owl's Pokémon/Pidgeotto-inspired crisp outlines, angular tufts, confident
> expressive poses and layered cel shading. Retain the species' real plumage
> or fur and distinguishing features. Full body, every wingtip, ear, foot and
> tail visible, with transparent margins. One animal on a genuinely transparent
> background. No scenery, gradient, glow, cast shadow, text, border or logo.

Bat prompts additionally specify mammalian faces, fur, finger-supported wing
membranes and each species' ear, noseleaf, muzzle and colour characteristics.
Four pose directions rotate through the collection: three-quarter stance,
banking flight, landing, and a side pose with a head turn.

Final files are local transparent WebP assets, up to 1200 pixels on the longest
edge (the two approved previews retain their original resolution). Each entry
in `chirpecho/web/static/species/artwork-manifest.json` records its source
generation filename, dimensions and final file checksum.

Run `python3 scripts/build_artwork_gallery.py` to rebuild contact sheets for review
and the legacy gallery bookmark. The bilingual live gallery is served at `/artwork`. These are stylised game illustrations, not
scientific identification drawings. Undiscovered cards use the same WebP artwork with a solid silhouette filter; the artwork gallery is an explicit preview of the entire set.

The mistle thrush and barn swallow were edited to remove an extra folded wing;
both now have exactly two wings. Corrected artwork uses content-versioned URLs.

## Pink-footed Goose (#071)

Generated with the built-in image generation tool and saved as
`chirpecho/web/static/species/bird-071-pokemon.webp`.

Prompt:

> Create one original creature-collecting game portrait for the Chirp & Echo bird atlas: a Pink-footed Goose (Anser brachyrhynchus). Crisp dark outlines, angular feather tufts, expressive confident pose and layered cel shading, Pokémon-inspired wildlife illustration. Full body three-quarter standing pose, both pink webbed feet fully visible, wings folded naturally. Accurate distinguishing plumage: dark chocolate brown head and relatively short neck, pale grey back with layered pale-edged feathers, buff pale unbarred breast and belly, white tail edge. Short dark black bill with a distinct pink band across the middle. No white forehead patch and no black belly bars. Plenty of transparent margin around all extremities. One animal on genuinely transparent background; no scenery, gradient, glow, cast shadow, text, border or logo.
