# Chirp & Echo artwork brief

Create a cohesive collection of expressive wildlife characters for the Bird
Atlas and Batlas: 98 birds and 24 bats. Each animal should have its own
personality while clearly belonging to the same set.

## Visual style

Use the original collection's crisp dark outlines, angular layered feathers and
restrained cel shading. Approved style anchors are Common Chaffinch (#007),
Eurasian Nuthatch (#023), European Goldfinch (#009), Redwing (#031), both sparrows
(#005–006), the swifts and the existing bats. Keep these approved drawings intact.
Match their eye construction, proportions, outline weight and feather detail.
Use neutral, alert or serious expressions; no smiles, oversized cute eyes or
invented fantasy crests. Retain recognisable species colours and markings.

## Poses and style revisions

Preserve the current pose, facing direction, wing and foot positions when revising
style. The new poses are wanted; style drift is not. Restore the original
Pink-footed Goose (#071) and Greater White-fronted Goose (#070) character designs
in their current poses. White-tailed Eagle (#065) must match the other birds of
prey. Starling (#012), Goldcrest (#028) and the warblers need the same finish as
the approved references. All Swifts and swallows (#037–039) must be airborne;
the Barn Swallow is the explicit exception to preserving the current pose.

Keep anatomy coherent: two wings, two legs and a natural neck position. Wings
should fold naturally at rest or move plausibly together in flight. Never use
the single raised wing in front of the body as a presentation gesture. Bat wings
must have finger-supported membranes and mammalian anatomy.

## Consistent presentation

One full-body animal, alone, on a genuinely transparent background. Keep all
exposed extremities inside the frame with comfortable margins. Naturally tucked
feet and occluded wings are fine.

Frame both bird and bat portraits on the same 1200 × 1200 transparent canvas.
Use the birds' visual scale for both collections: target 24% visible silhouette
area, capped at 1104 pixels in either direction for long wings, legs or tails.
Centre each silhouette and retain transparent margins. Run
`python3 scripts/normalize_artwork_framing.py` after accepting new artwork;
it skips assets already using this policy. This gives each species type a
consistent visual weight while accommodating natural differences in pose.
This framing adjustment must not change anatomy, expression or pose.

No props: no branches, twigs, bark, rocks, bricks, plants, food or objects in the
mouth. This includes the jay's former acorn. No scenery, gradient, glow, cast
shadow, text, border or logo.

## Base prompt

> Create one full-body [species] for the Chirp & Echo wildlife atlas. Match the
> collection's bold Pokémon-inspired character design, crisp dark outlines,
> angular tufts, expressive eyes and layered cel shading. Preserve [species
> markings]. Preserve [current natural pose] with a neutral alert expression. Keep anatomy
> coherent and the neck natural. One animal only, no props, on a genuinely
> transparent background, with every exposed extremity inside generous margins.
> No single raised presentation wing, scenery, glow, shadow, text or logo.

## Files and verification

Use the built-in image generation tool, one image per species. The final prompt
set is recorded in [artwork-personality-prompts.json](artwork-personality-prompts.json).
Save active portraits as `chirpecho/web/static/species/bird-NNN-pokemon.webp` or
`bat-NNN-pokemon.webp`, with transparency and a maximum edge of 1200 pixels.
Archived previews retain their original resolution.
Update `artwork-manifest.json` with the source filename, dimensions and checksum.

Review the collection together for style, anatomy, pose variety and stray props.
Run `python3 scripts/build_artwork_gallery.py` to rebuild review sheets. The
bilingual gallery is at `/artwork`, with dedicated Finches and Tits sections.
Gallery sections and species are alphabetised in the selected language. Combine
small types into named sections: ducks/geese/swans; cranes/cormorants/rails/waders;
bee-eaters/kingfishers/rollers; cuckoos/nightjars; long-eared bats/woodland
specialists; and horseshoe/cave bats. Search results retain their normal section.
Undiscovered cards
use silhouettes of the same artwork.

Additional pose variety: Little Owl (#045) now stands with both wings folded;
European Roller (#074) banks left in flight, and European Bee-eater (#075) glides
right with trailing tail streamers. These requested pose changes supersede the
pose-preservation instruction above for those three portraits. All remain alone,
prop-free and transparent. Their generation and refinement prompts are recorded
in `artwork-personality-prompts.json`, with checksums in the artwork manifest.
The unused legacy species SVGs have been removed; active portraits and locked
silhouettes both use the WebP artwork.

Latest requested revisions supersede the earlier pose-preservation instructions:
Pink-footed Goose (#071) walks with its head raised; Green Woodpecker (#022)
stands upright with folded wings; Blue Tit (#004) has a compact natural crown,
closed bill and stepping pose. Tawny Owl (#044) retains its spread-wing pose
on a square canvas with more transparent space and smaller eyes. The full
122-species collection was reviewed together for eye consistency; these four
replacements use restrained outlined eyes with a single highlight, retaining
species-specific iris colours and owl facial anatomy.

The next pose revisions use existing species as pose references only:
White-tailed Eagle (#065) follows Honey-buzzard (#068), Black-headed Gull (#053)
follows Barn Swallow (#038), Common Wood Pigeon (#018) follows Stock Dove (#064),
and Long-eared Owl (#046) follows Tawny Owl (#044). Preserve each target's own
plumage, anatomy, iris colour and identification markings.

Whooper Swan (#098), Dutch wilde zwaan, uses a proud trumpeting step and folded
wings. Its name and markings were checked against [BTO](https://www.bto.org/learn/about-birds/birdfacts/whooper-swan)
and [BirdNET](https://birdnet.cornell.edu/taxonomy/species/Cygnus%20cygnus); its
`whoswa` code matches [eBird](https://science.ebird.org/en/status-and-trends/species/whoswa/range-map).
