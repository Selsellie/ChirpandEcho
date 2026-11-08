"""Local BirdNET 2.4 inference through LiteRT, adapted to the archive worker."""
import os
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.special import expit
from chirpecho.chirp.catalogue import SPECIES
from chirpecho.chirp.labels import bird_labels


class BirdAPI:
    def __init__(self):
        from ai_edge_litert.interpreter import Interpreter
        directory=Path(os.environ.get('BIRD_MODEL_DIR','/opt/birdnet-v24'))
        self.labels=(directory/'labels.txt').read_text().splitlines()
        self.interpreter=Interpreter(model_path=str(directory/'model.tflite'),num_threads=int(os.environ.get('DETECTOR_THREADS','1')))
        self.interpreter.allocate_tensors()
        inputs=self.interpreter.get_input_details()
        outputs=self.interpreter.get_output_details()
        self.input=next(item for item in inputs if tuple(item['shape'])==(1,144000))
        self.output=next(item for item in outputs if int(item['shape'][-1])==len(self.labels))
        names={entry['scientific']:entry['name'] for entry in SPECIES}
        self.allowed=bird_labels(self.labels)
        if not set(names).issubset({label.split('_',1)[0] for label in self.labels}):
            missing=set(names)-{label.split('_',1)[0] for label in self.labels}
            raise ValueError('Bird catalogue has unsupported model labels: '+', '.join(sorted(missing)))

    def get_config(self,detection_threshold):
        return {'threshold':detection_threshold}

    def classify(self,audio):
        """Return scores for one complete 3-second, 48 kHz mono window."""
        if len(audio)!=144000 or not np.isfinite(audio).all():
            raise ValueError('Expected 144000 finite audio samples')
        span=float(np.max(audio)-np.min(audio))
        if span<1e-7:
            return np.zeros(len(self.labels),dtype=np.float32)
        normalized=((audio-np.min(audio))/span*2-1).astype(np.float32)
        self.interpreter.set_tensor(self.input['index'],normalized.reshape(1,-1))
        self.interpreter.invoke()
        # The official 2.4 acoustic TFLite model returns logits, not probabilities.
        return expit(self.interpreter.get_tensor(self.output['index'])[0])

    def process_file(self,filepath,config):
        audio,rate=sf.read(filepath,dtype='float32',always_2d=False)
        if rate!=48000 or audio.ndim!=1:
            raise ValueError('Bird recorder must provide mono 48 kHz audio')
        if len(audio)<144000:
            return {'pred_dict':{'annotation':[]}}
        offsets=list(range(0,len(audio)-144000+1,144000))
        if offsets[-1]+144000<len(audio):
            offsets.append(len(audio)-144000)
        annotations=[]
        for offset in offsets:
            scores=self.classify(audio[offset:offset+144000])
            for index,name in self.allowed.items():
                confidence=float(scores[index])
                if np.isfinite(confidence) and confidence>=config['threshold']:
                    annotations.append(dict(start_time=offset/48000,end_time=offset/48000+3,
                                            class_prob=confidence,det_prob=confidence,
                                            low_freq=0,high_freq=15000,**{'class':name}))
        return {'pred_dict':{'annotation':annotations}}
