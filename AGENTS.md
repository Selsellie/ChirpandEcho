# Species catalogue changes

When adding a species to the application, update the relevant milestone collecting
sets in `chirpecho/web/milestones.py` in the same change. Review membership,
checklists, artwork and targets, and update milestone descriptions in both English
and Dutch (`chirpecho/web/i18n.py`). Verify that the complete-atlas target follows
the catalogue size and that existing stored model labels resolve to the new entry.
Run the catalogue, collection and translation tests. Keep species groups, rarity,
portraits, the artwork manifest and species documentation consistent as well.
