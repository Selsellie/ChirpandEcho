# BirdNET acoustic model

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
