"""Write an independent audible stream from the one shared ultrasonic capture."""
import datetime as dt
import math
import os
from pathlib import Path
import uuid
import logging
from logging.handlers import RotatingFileHandler
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from chirpecho.common.runtime import ROOT, storage_available, write_status

log=logging.getLogger('chirp_recorder')


class BirdCapture:
    def __init__(self, sample_rate):
        if not log.handlers:
            directory=Path(os.environ.get('LOG_DIR',ROOT/'logs'))
            directory.mkdir(parents=True,exist_ok=True)
            handler=RotatingFileHandler(directory/'chirp_recorder.log',maxBytes=5*1024*1024,backupCount=3)
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
            log.addHandler(handler)
            log.propagate=False
        self.sample_rate=sample_rate
        self.output=Path(os.environ.get('BIRD_INCOMING_DIR','/audio/chirp'))
        self.output.mkdir(parents=True,exist_ok=True)
        self.checked=self.saved=self.dropped=0

    def process(self, audio, started_at):
        self.checked+=1
        divisor=math.gcd(self.sample_rate,48000)
        audible=resample_poly(np.asarray(audio).reshape(-1),48000//divisor,self.sample_rate//divisor).astype(np.float32)
        # A silent or broken input must not become high-confidence normalized noise.
        if not np.isfinite(audible).all() or np.max(np.abs(audible))<1e-7:
            self.status('silent')
            return False
        used = 0
        for path in self.output.rglob('*'):
            try:
                if path.is_file():
                    used += path.stat().st_size
            except FileNotFoundError:
                pass
        limit = int(os.environ.get('BIRD_MAX_AUDIO_MB', '24')) * 1024 ** 2
        if used + audible.size*2+4096 > limit or not storage_available(self.output,audible.size*2+4096):
            self.dropped+=1
            log.warning('Bird audio buffer full; dropping newest bird chunk')
            self.status('buffer_full')
            return False
        name=started_at.astimezone(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+uuid.uuid4().hex[:8]+'.wav'
        final=self.output/name
        temporary=final.with_name('.'+name+'.tmp')
        try:
            sf.write(temporary,audible,48000,format='WAV',subtype='PCM_16')
            temporary.replace(final)
        finally:
            temporary.unlink(missing_ok=True)
        self.saved+=1
        log.info('wrote %s',name)
        self.status('listening')
        return True

    def status(self,state):
        write_status('chirp_recorder',state=state,checked=self.checked,retained=self.saved,
                     dropped=self.dropped,sample_rate=48000,source='Shared Vleermic capture')
