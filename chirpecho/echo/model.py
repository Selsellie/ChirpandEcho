"""Echo's BatDetect2 adapter; the bird worker never imports PyTorch."""
import os
import torch

torch.set_num_threads(int(os.environ.get('DETECTOR_THREADS', '2')))
torch.set_num_interop_threads(1)
from batdetect2 import api


def get_config(**options):
    return api.get_config(**options)


def process_file(filepath, config):
    return api.process_file(filepath, config=config)
