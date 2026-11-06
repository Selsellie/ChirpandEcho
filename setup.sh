#!/usr/bin/env bash
# Bootstraps one shared environment for the recorder, detector, and dashboard.
# Run from the BatsDropping project root: ./setup.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo ">>> Installing system packages (apt)..."
sudo apt-get update
grep -vE '^\s*#|^\s*$' apt-packages.txt | sudo xargs apt-get install -y

echo ">>> Creating an isolated virtualenv..."
python3 -m venv venv

echo ">>> Installing pip packages into venv..."
echo ">>> (batdetect2 pulls in torch - if this starts building from source"
echo ">>> instead of downloading a wheel, stop and flag it, don't wait it out)"
source venv/bin/activate
pip install --only-binary=:all: -r requirements.txt
pip check
pip freeze > requirements.lock.txt

echo ">>> Verifying environment..."
python3 -c "
import importlib.metadata
import numpy, scipy, sounddevice, soundfile, matplotlib, flask
from batdetect2 import api
print('numpy      ', numpy.__version__)
print('scipy      ', scipy.__version__)
print('sounddevice OK')
print('soundfile   OK')
print('matplotlib  OK')
print('flask       ', importlib.metadata.version('flask'))
print('batdetect2  OK')
"

echo ">>> Done. Activate with: source venv/bin/activate"
echo ">>> Recorder: python3 recorder/recorder.py"
echo ">>> Detector: python3 detector/detector.py"
echo ">>> See README.md for local development commands."
