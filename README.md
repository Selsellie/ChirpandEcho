<img width="373" height="74" alt="image" src="https://github.com/user-attachments/assets/3a350c67-b19c-463f-9432-717216c29750" />


**A little eavesdropping on the night shift.**

I built BatsDropping to find out who’s fluttering around after sunset.
It captures ultrasonic activity, looks for bat calls
with [BatDetect2](https://github.com/macaodha/batdetect2), and turns detections
into species predictions, timestamps, confidence scores, and spectrograms.
My ears miss the conversation. BatsDropping takes notes.

## An extra pair of ears: Vleermic 🎙️

I use a **Vleermic USB 384 kHz ultrasonic microphone** to pick up the
high-frequency sounds bats make. This project has been tested with that
microphone, with a default recording rate of **384 kHz**.

An ordinary microphone generally won’t capture these ultrasonic frequencies. Another
ultrasonic microphone may work, provided it supports the configured sample
rate and the input settings are adjusted for it.

## What’s in the bat bag?

- **An ear for brief calls.** Short activity windows help catch quick signals
  inside five-second audio chunks.
- **A bat-call detective.** BatDetect2 searches candidate audio for calls and
  predicts their species.
- **A little breathing room.** A ten-second cooldown follows each saved
  activity chunk, reducing how much audio needs to be processed on busy nights.
- **Pictures of sound.** PNG spectrograms show the frequency and timing of
  each retained call.
- **Field notes that stick around.** SQLite keeps species predictions,
  timestamps, confidence scores, call probabilities, and frequency ranges.
- **Some storage housekeeping.** Older images make way when space runs low,
  while their observation data stays in the archive.

## From flutter to field note

1. **Listen:** the Vleermic continuously captures ultrasonic audio.
2. **Spot some activity:** the gate selects candidate chunks.
3. **Investigate:** BatDetect2 looks for calls and predicts their species.
4. **Take notes:** qualifying detections become database records and PNGs.
5. **Have a look:** the dashboard brings the encounters and their images together.

The activity gate can also react to other ultrasonic sounds. A trigger doesn’t
automatically mean “bat spotted!” The cooldown starts when an activity chunk
is saved, before classification confirms whether there are any qualifying calls.

## A window into the night 🌙

The dashboard makes the field notes easy to explore, with:

- A spectrogram gallery with larger image previews.
- Species search and confidence filters.
- Pages of past encounters to browse.
- Activity charts, species summaries, and confidence statistics.
- A detection ledger with timestamps, frequencies, and call probabilities.
- Microphone, processing, and storage status.
- A remembered light, dark, or system appearance setting.
- A Logs tab with recent recording and classification summaries, warnings,
  and explanations when a recording contains no qualifying bat calls.
- A Health tab checking recorder and detector heartbeats, database access,
  and storage reserves. Healthy services do not guarantee bat activity.
- Batlas, a searchable collection of 24 Western European bat species with
  habitat notes and conservation sources. Retained predictions unlock cards
  and show call counts, first/last records, and best confidence. The seven
  species outside the bundled classifier are marked as field guide entries.
- A clear note when an image has been cleared but its observation data remains.

## The detective work stays local

Classification stays local. BatDetect2 uses its bundled model, and
BatsDropping does not upload recordings to a cloud classification service.
Once the software is installed, listening, classification, image generation,
and dashboard use do not require an Internet connection. Installing or
updating dependencies may require downloads.

The dashboard uses local assets, without external fonts, scripts, or
analytics. Network access controls are separate from the processing code;
local inference alone does not enforce a network block.

## No mountain of WAVs

Audio waits temporarily in **RAM** instead of building a permanent WAV
collection. Successfully processed audio is deleted. Failed or pending audio
stays in a bounded retry buffer and expires after ten minutes by default.
Unprocessed audio can be lost on a restart or power failure.

The lasting collection is **PNG spectrograms and detection metadata**. By
default, image cleanup starts at **85% disk usage** and aims for **80%**.
A **1 GiB free-space reserve** also triggers cleanup. The oldest images go
first, but their species, timestamps, confidence scores, and frequency data
remain searchable. Optional age-based image expiry is disabled by default.

If there’s still no room after the images have been cleared, new recording
and processing pause until space becomes available. Even bat field notes
need somewhere to live.

## A small reality check

Species labels are predictions, not confirmed sightings. Microphone
placement, recording quality, background noise, and the classifier all affect
the result. Confidence scores are useful clues when reviewing an encounter.

Busy nights also mean more work. The buffer, cooldown, and storage limits help
manage demand, but heavy activity can still delay results or cause audio
chunks to be discarded.

## Under the wings

Built with Vleermic, Python, BatDetect2, PyTorch, NumPy, SciPy, sounddevice,
SoundFile, Matplotlib, SQLite, Flask, and Gunicorn.

Happy Batsdropping!
