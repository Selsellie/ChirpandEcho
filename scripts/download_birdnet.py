#!/usr/bin/env python3
"""Build-time-only verified download; inference never downloads model files."""
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.request
import zipfile

URL='https://zenodo.org/records/15050749/files/BirdNET_v2.4_tflite.zip'
SHA256='31377e128d86fe7b65fa91b206b8804bad1cd934e624bbe6e7c1788170c95e57'


def install(destination,archive=None):
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        source=Path(archive) if archive else Path(work)/'birdnet.zip'
        if archive is None:
            with urllib.request.urlopen(URL,timeout=120) as response,source.open('wb') as target:
                shutil.copyfileobj(response,target)
        with source.open('rb') as handle:
            digest=hashlib.file_digest(handle,'sha256').hexdigest()
        if digest!=SHA256:
            raise ValueError('BirdNET archive checksum mismatch')
        with zipfile.ZipFile(source) as bundle:
            for member,name in [('audio-model.tflite','model.tflite'),('labels/en_uk.txt','labels.txt')]:
                with bundle.open(member) as incoming,(destination/name).open('wb') as outgoing:
                    shutil.copyfileobj(incoming,outgoing)
        (destination/'SOURCE.txt').write_text('BirdNET acoustic model 2.4\n'+URL+'\nSHA256 '+SHA256+'\nModel license: CC BY-NC 4.0\nhttps://zenodo.org/records/15050749\n')


if __name__=='__main__':
    install(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
