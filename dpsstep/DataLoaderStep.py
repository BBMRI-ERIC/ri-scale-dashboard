from __future__ import annotations
from pathlib import Path

import torch


from .DPSStep import DPSStep

class DataLoaderStep(DPSStep):
    def __init__(self, name: str = "Data Loader"):
        super().__init__(name)

    def execute(self, data) -> torch.utils.data.Dataset:
        raise NotImplementedError("DataLoaderStep execute method must be implemented in subclasses.")

