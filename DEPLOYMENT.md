# Deployment

### Give the observatory a home 🛠️

I run Chirp & Echo on an ARM64 Raspberry Pi with Linux, K3s, and a Vleermic.
My deployment script builds the image with Podman, imports it into K3s, backs up
both databases, applies the manifest, and restarts the app.

Supply your own Kubernetes or Compose configuration for the four containers,
shared storage, device permissions, and LAN access. Docker/Compose deployment
has not been tested. The image's default command starts only the website.

### Build the image

Pack both wildlife detectives into one image. Run this from the project root:

```bash
podman build -f Containerfile -t chirp-echo .
```

Make the image available to your container runtime before starting the services.
For my K3s deployment, that means importing the built image into K3s.

### Containers and storage

One image, four jobs. Meet the observatory crew:

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

### Discord notifications (optional)

Give new discoveries somewhere to take a bow. Configure **both detector
containers** with either `DISCORD_WEBHOOK_URL` or `DISCORD_WEBHOOK_URL_FILE` (a mounted secret file containing the URL). The file
setting takes precedence. Without a webhook, notifications are disabled. Keep
the URL in a secret rather than source control: it grants permission to post to
your Discord channel.

Create an incoming webhook for your chosen Discord channel and copy its URL
into a local secret file. For Kubernetes, create a Secret from that file:

```bash
kubectl -n YOUR_NAMESPACE create secret generic chirp-echo-discord \
  --from-file=url=/path/to/discord-webhook-url
```

Git does not remove secrets automatically. Only the Secret reference belongs in
your deployment manifest; do not commit the webhook URL, its local file, or an
export of the Kubernetes Secret. A Git push does not copy the cluster's Secret;
create it separately when setting up another installation.

Add this environment entry to each detector container:

```yaml
env:
  - name: DISCORD_WEBHOOK_URL
    valueFrom:
      secretKeyRef:
        name: chirp-echo-discord
        key: url
```

The detector pods need DNS access and outbound HTTPS to Discord. My deployment
adds an explicit exception to its default-deny egress policy for cluster DNS and
public HTTPS. Standard Kubernetes NetworkPolicy filters addresses and ports, not
hostnames; this permits public HTTPS beyond Discord as well. Classification and
audio processing still run locally; the webhook sends only notification metadata,
never audio.

### Start and update

Time to open the listening post. After configuring the containers, storage,
and optional Discord webhook, apply your deployment configuration and start
all four services. Open the dashboard
on port **8090** and check its **Health** and **Logs** pages for both pipelines.

For updates, back up both SQLite archives, build and load the new image, then
restart the services with their persistent storage and Secret references intact.
The Discord Secret is configured separately from the image and Git checkout.

## Recording retention and storage

WAVs that produce a saved prediction are copied from the RAM buffer to each
archive's `audio` directory on persistent storage. They expire after 24 hours.

| Setting | Default | Purpose |
| --- | --- | --- |
| `AUDIO_ARCHIVE_TTL_SECONDS` | `86400` | Maximum clip age. |
| `AUDIO_ARCHIVE_MAX_MB` | `512` | Per-pipeline cap; oldest clips may expire earlier. |
| `AUDIO_BUFFER_TTL_SECONDS` | `600` | Pending/failed RAM buffer expiry. |
| `MIN_FREE_MB` | `1024` | Free-space reserve. |
| `STORAGE_HIGH_WATER_PERCENT` | `85` | Start spectrogram cleanup. |
| `STORAGE_LOW_WATER_PERCENT` | `80` | Cleanup target. |

Recordings without saved predictions are discarded after processing. Pending
audio in RAM can be lost during a restart or power failure. Spectrogram cleanup
preserves detection metadata. Explicit encounter deletion removes the selected
record, its spectrogram, and its WAV if no other encounter shares that recording.

## Dashboard

Use **Logs** with the bird/bat switch to inspect each pipeline. **Health** shows
both services and the **A lighter footprint** storage panel. The **Artwork** tab
supports the same English/Dutch switch as the rest of the website.

Back to the [README](README.md).
