import torch
from torch.utils.data import DataLoader
from torch.utils.data._utils.collate import default_collate
import numpy as np
import openslide
from collections import defaultdict



class SVSLoader(DataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slide_cache = defaultdict(openslide.OpenSlide)
