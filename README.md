<img width="346" height="86" alt="image" src="https://github.com/user-attachments/assets/e8c89b2e-0179-4b39-afbd-5e93ab15a349" />


**Birds by song. Bats by echo. A little eavesdropping on both shifts.**

I made Chirp & Echo to record all the birds and bats in and around my house.
I wanted to find out who visits during the day, who flies past at night, and
build a lasting record of the wildlife sharing my home and garden.

**Chirp** listens for
birdsong with BirdNET 2.4; **Echo** looks for bat calls with BatDetect2.
Together they turn microphone recordings into species predictions, timestamps,
confidence scores, and pictures of sound.

My ears miss half the conversation. Chirp & Echo takes notes.

## An extra pair of ears: Vleermic 🎙️

I use a **Vleermic USB 384 kHz ultrasonic microphone** on a Raspberry Pi.
One microphone feeds both listeners: an audible stream for Chirp and an
ultrasonic stream for Echo. No microphone custody battle required.

The default recording rate is **384 kHz**. Another microphone may work if it
supports the configured input settings; an ordinary microphone generally
won’t capture the ultrasonic frequencies Echo needs.

## What’s in the field bag?

- **Two wildlife detectives.** BirdNET listens for birds; BatDetect2 searches
  candidate recordings for bat calls.
- **An ear for brief calls.** Echo checks short activity windows inside each
  five-second chunk, helping catch quick ultrasonic signals.
- **A little breathing room.** Echo takes a ten-second cooldown after saving
  an activity chunk. Chirp keeps getting audio regardless of that cooldown.
- **Pictures of sound.** PNG spectrograms let you inspect retained predictions.
- **Field notes that stick around.** Separate SQLite archives keep the bird
  and bat predictions, timestamps, confidence scores, and processing details.
- **Some storage housekeeping.** Older images make way when space runs low,
  while their detection records stay in the archive.

## From flutter or tweet to field note

1. **Listen:** the shared recorder captures five-second chunks at 384 kHz.
2. **Split the conversation:** Chirp gets a filtered, resampled 48 kHz copy
   before Echo’s gate or cooldown is applied.
3. **Investigate:** Echo checks activity between 15 and 100 kHz and sends
   candidate chunks to BatDetect2. BirdNET analyses Chirp’s audio in
   three-second windows.
4. **Take notes:** qualifying predictions become database records and
   spectrograms. My deployment retains bird predictions at 70% confidence
   or higher.
5. **Have a look:** the dashboard brings both collections together.

Both listeners run continuously. Switching the website view changes what
you see, not who’s on microphone duty.

Echo’s activity gate can react to other ultrasonic sounds, so a trigger
doesn’t automatically mean “bat spotted!” Its cooldown starts when audio is
saved, before classification confirms any qualifying calls. Chirp’s windows
can overlap, so its counts are predictions, not individual calls or birds.

## A window into the wings 🌙

The dashboard gives each listener its own **Detections** and **Species** views,
with shared **Logs** and **Health** pages:

- Browse spectrograms, open larger previews, and page through past encounters.
- Search species and filter predictions by confidence.
- Explore activity charts, species summaries, and detection details.
- Check recent recording and classification summaries, including warnings
  and recordings with no qualifying predictions.
- Inspect recorder and classifier heartbeats, database access, and storage.
  Healthy services don’t guarantee wildlife activity.
- Choose light, dark, or system appearance and let the dashboard remember it.
- Keep browsing the field notes even after an older image has been cleared.

The species collection has **24 Western European bats** and a starter list of
**56 Western European birds**, with habitat notes and recorded activity.
Some bat cards are field guide entries outside the bundled model’s abilities;
those are marked. The birds are a selection, not a complete regional checklist.
A card in the guide doesn’t mean its owner has visited the microphone.

## A Pokédex for the wildlife around my house

I borrowed the collection idea from Pokémon’s **Pokédex**: discover a species,
unlock its entry, and gradually fill the collection with real birds and bats.
Each of the 80 guide species has its own cartoon portrait and custom description.
Undiscovered species appear as dark silhouettes; their colours, descriptions,
and field notes are revealed after a retained detection unlocks the card.

It gives me a playful reason to keep listening and learn about each visitor.
The discoveries are classifier predictions rather than confirmed sightings,
and the counts represent detection records, not individual animals.

## No mountain of WAVs

Audio waits temporarily in **RAM**, rather than becoming a permanent recording
collection. Successfully processed WAVs are deleted. Pending or failed audio
uses a bounded buffer and expires after ten minutes by default. Unprocessed
audio can be lost on a restart or power failure.

The lasting collection is **PNG spectrograms and detection metadata**.
By default, image cleanup starts at **85% disk usage**, aims for **80%**, and
also protects a **1 GiB free-space reserve**. Each archive clears its oldest
images first while keeping the detection records. Optional age-based image
expiry is disabled by default.

When buffers fill, new chunks can be dropped; when disk space is too low,
recording and processing can pause. Even wildlife gossip needs somewhere to live.

## The detective work stays local

Inference runs locally; audio isn’t uploaded to a classification service.
BirdNET’s model and labels are downloaded and checksum-verified during the
image build. Runtime inference doesn’t need Internet access.

The dashboard uses local assets, without external fonts, scripts, or analytics.
My Kubernetes configuration limits incoming access to the LAN and monitoring,
and blocks outbound pod connections. Those network controls belong to the
deployment; the image alone doesn’t enforce them.

## A small reality check

Species labels are predictions, not confirmed sightings. Microphone placement,
recording quality, background noise, and the models all affect the results.
Confidence scores are clues for reviewing an encounter, not proof of a visit.

Busy mornings and busy nights also mean more work. Buffers and cooldowns help
manage demand, but heavy activity can delay results or cause audio to be dropped.

## Project structure

```text
Chirp&Echo/
├── chirpecho/
│   ├── capture.py          # shared microphone service
│   ├── worker.py           # shared classification/archive worker
│   ├── common/             # logging, status, storage limits and image cleanup
│   ├── chirp/              # audible audio, BirdNET adapter and bird catalogue
│   ├── echo/               # ultrasonic gate, BatDetect2 adapter and bat catalogue
│   └── web/                # Flask app, templates and static assets
├── scripts/
│   └── download_birdnet.py # verified model download during the image build
├── Containerfile
├── requirements.txt        # direct application dependencies
├── requirements.lock.txt   # pinned base dependencies
├── THIRD_PARTY.md
└── data/                   # ignored live data, outside the image
```

Chirp's additional inference dependencies are pinned in
`chirpecho/chirp/requirements.lock.txt` and installed as a separate image layer.

## Containers and storage

One image runs as four containers:

| Container | Command | Role |
| --- | --- | --- |
| Recorder | `python -m chirpecho.capture` | Owns the microphone and writes both audio queues. |
| Echo detector | `python -m chirpecho.worker --watch` | Uses BatDetect2 by default. |
| Chirp detector | Same worker, with `DETECTOR_ENGINE=bird` | Uses the bundled BirdNET model. |
| Website | Image default: Gunicorn serving `chirpecho.web.app:app` | Reads the archives and serves port 8090. |

Containers share persistent `/data`, a RAM-backed `/audio` volume, and `/status`
for heartbeats. Only the recorder needs microphone access through `/dev/snd`.
Configure `BIRD_ENABLED=1` on the recorder to feed Chirp. Each detector needs its
own inbox and archive paths:

| Pipeline | Audio inbox | Database | Spectrograms |
| --- | --- | --- | --- |
| Echo | `/audio/incoming` | `/data/db/detections.sqlite3` | `/data/detections` |
| Chirp | `/audio/chirp` | `/data/chirp/db/detections.sqlite3` | `/data/chirp/detections` |

Set `INCOMING_DIR`, `DB_PATH`, and `DETECTIONS_DIR` per detector. The website uses
`BIRD_DB_PATH` and `BIRD_DETECTIONS_DIR` to locate Chirp's archive. Mounted directories
must be writable by UID/GID 1000; read-only containers also need writable `/tmp`.

## How to deploy

I run Chirp & Echo on an ARM64 Raspberry Pi with Linux, K3s, and a Vleermic.
My deployment script builds this Containerfile with Podman, imports the image
into K3s, backs up both databases, applies the manifest, and restarts the app.

To build the image yourself, run this from the project root:

```bash
podman build -f Containerfile -t chirp-echo .
```

Supply your own Kubernetes or Compose configuration for the four containers,
shared storage, device permissions, and LAN access. The image’s default command
starts only the website. Docker/Compose deployment has not been tested.

## A nod to our wildlife detectives

BirdNET was developed by the K. Lisa Yang Center for Conservation Bioacoustics
at the Cornell Lab of Ornithology and Chemnitz University of Technology. The
[BirdNET 2.4 model](https://zenodo.org/records/15050749) is published under
**CC BY-NC 4.0**, separately from this application’s code.

Echo’s bat detective is [BatDetect2](https://github.com/macaodha/batdetect2/tree/v1.3.1),
developed by Oisin Mac Aodha, Santiago Martínez Balvanera, and collaborators.
The project uses version 1.3.1 and its bundled pretrained UK bat model;
the [upstream licence](https://github.com/macaodha/batdetect2/blob/v1.3.1/LICENSE.md)
is **CC BY-NC 4.0**. Their research is described in
[Towards a General Approach for Bat Echolocation Detection and Classification](https://www.biorxiv.org/content/10.1101/2022.12.14.520490v1)
(Mac Aodha et al., 2022).

See [THIRD_PARTY.md](THIRD_PARTY.md) for attribution and licence details
for both listeners.

## Under the wings

Built with Vleermic, Python, BirdNET, LiteRT, BatDetect2, PyTorch, NumPy, SciPy,
sounddevice, SoundFile, Matplotlib, SQLite, Flask, and Gunicorn.

Happy Chirping & Echoing!
