<img width="346" height="86" alt="Chirp & Echo logo" src="https://github.com/user-attachments/assets/e8c89b2e-0179-4b39-afbd-5e93ab15a349" />

**Birds by song. Bats by echo. A wildlife guestbook for my home.**

I built Chirp & Echo to discover the birds and bats in and around my house.
Who is singing outside the window? Who flies past after sunset?
One Raspberry Pi listens; the neighbours supply the soundtrack.

## One observatory. Two worlds. 🎙️

**Chirp** recognises birdsong with BirdNET 2.4. **Echo** searches for bat calls
with BatDetect2. My Vleermic captures at 384 kHz; Chirp gets a separate 48 kHz
stream. Both listeners run continuously, whichever page is open.

Saved predictions become a collection of species, recordings, timestamps,
confidence scores and interactive spectrograms. Identification runs locally.
Predictions are clues to review, rather than confirmed sightings or animal counts.

## Find your way around 🧭

| Tab | What you can explore |
| --- | --- |
| **Detections** | Recent encounters with species portraits, confidence, timestamps, playback and spectrograms. |
| **Species** | The Bird Atlas and Batlas: discover species, unlock artwork and read field notes. |
| **Calendar** | A shared bird-and-bat diary with daily activity, encounters and weekly reports. |
| **Milestones** | Illustrated achievements, collecting sets and checklists for birds and bats. |
| **Artwork** | The full illustration gallery, with a Chirp/Echo selector and species search. |
| **Logs** | Follow the selected bird or bat pipeline through capture and classification. |
| **Health** | Check both pipelines, their archives and available storage. |

Chirp and Echo share a consistent introduction and navigation. Calendar,
Milestones and Health bring both worlds together without a bird/bat selector.
The interface supports **English and Dutch**, with **light, dark and system**
appearance options.

## A Pokédex outside the window 

I borrowed Pokémon's **Pokédex** idea: discover a species and unlock its card.
No tall grass required, just a microphone and some chatty neighbours.

- **70 birds and 24 bats** in the starter field guides. See the
  [full roster, model support and rarity tiers](SPECIES.md).
- **94 individual illustrations** with lively Pokémon-inspired artwork on
  transparent backgrounds. Undiscovered cards use matching silhouettes.
- **Field notes to unlock:** a retained prediction reveals a species' colours
  and description. Bird cards link to eBird; bat cards link to species references.
- **Rarity stars:** Common, Uncommon, Rare, Epic and Legendary are collection-game
  tiers, rather than measures of local abundance or conservation status.

BirdNET can also recognise birds outside the starter catalogue. Qualifying bird
predictions are saved and marked **“Not in catalogue — needs to be added.”**
The Bird Atlas lists them under **“Birds to add to the catalogue”**, ready for
identification review and a future atlas entry. They do not automatically unlock
or create a catalogue card. Non-bird model labels are excluded.

## A diary from dawn to dusk 📅

The **Calendar** combines both archives into one listening diary. Browse weeks
with the arrows or date picker, then select a day from the compact week strip.

- **Your chosen day:** bird and bat prediction totals, with a simple hourly
  activity chart showing when each was heard.
- **Familiar encounter cards:** up to 30 recent predictions for that day, using
  the same portraits, confidence scores, playback and signal links as Detections.
- **An expandable weekly report:** Monday–Sunday totals, species count, active
  days, the busiest day, first-time discoveries and the most-heard species.

Dates follow the configured local time zone, Europe/Amsterdam by default.
Reports include existing saved history. A quiet day can also mean the recorder
was offline; the diary records predictions, not recording coverage.

## Little discoveries, illustrated milestones 🏅

The **Milestones** page brings together **37 illustrated achievements**. Cards
use the same colourful bird and bat portraits as the collection, with progress
bars and expandable checklists showing which species you have and which are
still missing.

**12 bird collecting sets** include the tit club, goose parade, owl patrol,
crow crew, woodpecker duo, finch party, thrush choir, daytime birds of prey,
pigeons and doves, sparrows, waterside birds and sky acrobats.

**5 bat collecting sets** cover pipistrelles, open-air hunters, Myotis bats,
long-eared bats and horseshoe bats. Bat checklists target species supported by
the bundled classifier: 17 of the 24 species in the field guide.

**20 listening achievements**, split between birds and bats, celebrate first
predictions, growing collections, busy days, seven-day listening streaks,
30 active days, 1,000 and 10,000 predictions, and completing each supported atlas.
Bird and bat goals track their own progress, so bird recordings cannot unlock
bat achievements.

Each species counts once in a collecting set, even if it has been heard many
times or stored under different recognised labels. Sets are playful collection
themes; their checklists define the members.

Reports and milestones use retained detection metadata. Clearing recordings or
spectrograms for space preserves progress; explicitly deleting observations can
change it.

## Take a look, then take a listen 

Open an encounter's **Signal** to explore its spectrogram, recording time and
frequency. Use **Listen** to replay the saved WAV while it remains available.
The observation register adds model, sample rate, call duration, frequency,
source filename and storage timestamp. Bird entries show the model analysis
band, rather than a measured call-frequency range; older records may lack some
metadata.

Recordings with saved predictions have no age or archive-size limit. When disk
space runs low, the oldest recordings are removed first, and spectrograms can
also be cleared. Detection metadata stays. To remove an encounter explicitly,
use its **⋯** menu and confirmation step.

The **Artwork** gallery reveals the whole illustration collection for browsing,
including undiscovered species. Switch between **Chirp · Birds** and
**Echo · Bats**, search by species name, and open any image at full size.
Compact cards show **five illustrations per row** on wide screens, with fewer
columns on smaller devices.

## A new species has entered the chat 

Optional Discord webhooks announce **only the first discovery of each species**.
Birds and bats get different English messages with confidence and rarity stars.
Birds outside the catalogue include a notice that an entry needs to be added.
Existing records count as already discovered; repeat predictions do not trigger
another welcome.

Inference and recordings stay local. Discord receives notification metadata,
never audio.

## Open the listening post 

My setup runs on an **ARM64 Raspberry Pi with Linux, K3s and a Vleermic**.
A shared container image powers microphone capture, both classifiers and the
website, which serves port **8090**.

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for building the image, configuring the
four services, microphone access, persistent storage, updates and optional
Discord Secret configuration. Supply your own deployment manifests. Keep webhook
URLs and other secrets outside the checkout.

## A nod to the wildlife detectives 💚

Thanks to BirdNET, BatDetect2, their researchers and the open-source tools behind
this listening post. Model licences and attribution are in
[THIRD_PARTY.md](THIRD_PARTY.md). The [artwork brief](scripts/artwork-brief.md)
documents the illustration direction.

Happy chirping, happy echoing, and may your next visitor unlock a new card!
