# Species catalogue changes

When adding a species to the application, update the relevant milestone collecting
sets in `chirpecho/web/milestones.py` in the same change. Review membership,
checklists, artwork and targets, and update milestone descriptions in both English
and Dutch (`chirpecho/web/i18n.py`). Verify that the complete-atlas target follows
the catalogue size and that existing stored model labels resolve to the new entry.
Run the catalogue, collection and translation tests. Keep species groups, rarity,
portraits, the artwork manifest and species documentation consistent as well.

# Species browsing and artwork

Keep the Species type filter and Artwork sections on the shared `artwork_group()`
helper in `chirpecho/web/artwork.py`. Preserve each bird's native species type
in the catalogue and on its card (for example Starlings), and map that type to
its broader browsing section (for example Crows, jays and starlings). Use the
15 agreed bird sections and five bat sections documented in `SPECIES.md`.
Sort sections alphabetically in the selected language. Filtering must not change
group membership. Milestones remain independent scientific-name checklists.

Keep all reusable and species-specific artwork prompts, including eye revisions,
in `scripts/artwork-prompts.json`. Use `scripts/artwork-brief.md` for art direction
and asset workflow. Display the source illustrations directly without an added outer-outline filter.
Keep the solid silhouette filter for undiscovered species.
