<img width="346" height="86" alt="Chirp & Echo logo" src="https://github.com/user-attachments/assets/e8c89b2e-0179-4b39-afbd-5e93ab15a349" />

**Birds by song. Bats by echo. A wildlife guestbook for my home.**

I built Chirp & Echo to record all the birds and bats in and around my house.
Who is singing outside the window? Who flies past after sunset?
One Raspberry Pi listens; the neighbours supply the soundtrack.

## Two detectives, one microphone 🎙️

**Chirp** recognises birdsong with BirdNET 2.4. **Echo** searches for bat calls
with BatDetect2. My Vleermic captures at 384 kHz; Chirp gets a separate 48 kHz
stream. Both listeners run continuously, whichever page is open.

Predictions become timestamps, confidence scores and interactive spectrograms.
They are clues to review, rather than confirmed sightings or animal counts.

## A Pokédex outside the window ✨

I borrowed Pokémon's **Pokédex** idea: discover a species and unlock its card.
No tall grass required—just a microphone and some chatty neighbours.

- **69 birds and 24 bats:** browse the [full roster and rarity tiers](SPECIES.md).
- **93 individual illustrations:** lively Pokémon-inspired artwork on transparent backgrounds.
- **Matching silhouettes:** undiscovered cards use the exact same artwork outline.
- **Unlock the field notes:** colours and descriptions appear after a saved prediction.
- **Rarity stars:** Common, Uncommon, Rare, Epic and Legendary are collection-game tiers.
  They describe the game, not local abundance or conservation status.

## Take a look, then take a listen 🌿

- **Recent encounters:** picture-left rows with room to read, confidence and timestamps.
- **Signals on demand:** open a spectrogram for actual recording time and frequency in kHz.
- **Listen again:** prediction WAVs stay available for 24 hours in a bounded local archive.
  The 512 MiB cap per pipeline can clear older clips earlier when full.
- **Quiet housekeeping:** encounter deletion lives under **⋯**, with a confirmation step.
- **Artwork tab:** browse every illustration, filter birds/bats and search species names.
- **English or Dutch:** the language switch also translates artwork names and gallery controls.
- **Logs:** use the bird/bat switch to follow the selected listener's activity.
- **Health:** service checks and **A lighter footprint** keep storage in view.
- **Your preferred view:** light, dark or system appearance; bird pages get treetops.
- **More field help:** bird cards link to eBird; bat cards link to bat references.

The Artwork gallery deliberately reveals the whole set for browsing.
The species collection keeps undiscovered entries hidden until a prediction unlocks them.

## A new species has entered the chat 📣

Optional Discord webhooks announce **only the first discovery of each species**.
Birds and bats get different English messages, including confidence and rarity stars.
Existing records count as already discovered; repeats do not trigger another welcome.

Inference and recordings stay local. Discord receives notification metadata, never audio.

## Open the listening post 🛠️

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for the container setup, microphone access,
storage, updates and Discord Secret configuration. The website runs on port **8090**.
Git does not strip secrets: keep the webhook URL outside your checkout.

## A nod to the wildlife detectives 💚

Thanks to BirdNET, BatDetect2, their researchers and the open-source tools behind
this listening post. Model licences and attribution are in [THIRD_PARTY.md](THIRD_PARTY.md).
The [artwork brief](scripts/artwork-brief.md) documents the illustration direction.

Happy chirping, happy echoing—and may your next visitor unlock a new card!
