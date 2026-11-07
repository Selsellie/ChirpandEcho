# Third-party acknowledgements

## BirdNET acoustic model

Chirp uses the BirdNET 2.4 acoustic model developed by the K. Lisa Yang Center
for Conservation Bioacoustics at the Cornell Lab of Ornithology and Chemnitz
University of Technology. The model and label files are downloaded during the
container build from the authors' fixed Zenodo record:

https://zenodo.org/records/15050749

That record publishes the model under Creative Commons Attribution
NonCommercial 4.0 (CC BY-NC 4.0):

https://creativecommons.org/licenses/by-nc/4.0/

The model's licence is separate from the application code. The image includes
`/opt/birdnet-v24/SOURCE.txt` with its source URL, archive checksum and licence.
The original model weights are used without retraining. The application filters
predictions to a documented starter list and converts model logits into scores.

## BatDetect2 bat detector

Echo uses **BatDetect2 1.3.1**, developed by Oisin Mac Aodha, Santiago
Martínez Balvanera, and collaborators, to detect and classify bat echolocation
calls. The application installs the upstream Python package and uses its
bundled pretrained UK bat model locally, without retraining or modifying
the model weights.

- Source and version: [BatDetect2 v1.3.1](https://github.com/macaodha/batdetect2/tree/v1.3.1).
- Upstream licence: [LICENSE.md at v1.3.1](https://github.com/macaodha/batdetect2/blob/v1.3.1/LICENSE.md),
  Creative Commons Attribution-NonCommercial 4.0 International
  ([CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)).
- Research reference: Oisin Mac Aodha et al. (2022),
  [Towards a General Approach for Bat Echolocation Detection and Classification](https://www.biorxiv.org/content/10.1101/2022.12.14.520490v1).

The upstream licence applies to the BatDetect2 materials distributed with
the application, separately from this application's own code. Chirp & Echo
adds activity gating, confidence filtering, storage, and dashboard views
around the upstream detector. BatDetect2 is supplied without warranties;
see the upstream licence for its full terms and disclaimer.
