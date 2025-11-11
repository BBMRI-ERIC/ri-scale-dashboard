import openslide
import torch
from torch.utils.data import Dataset
import numpy as np

class SVSDatasetSingleSlide(Dataset):
    def __init__(self, data_path: str, patch_size=(512, 512), labels=None):
        self.slide = openslide.OpenSlide(data_path)
        self.patches = self._load_patches(patch_size)
        self.labels = labels

    def _load_patches(self, patch_size):
        patches = []
        level_dims = self.slide.level_dimensions[0]
        pw, ph = patch_size
        for ly in range(0, level_dims[1], ph):
            for lx in range(0, level_dims[0], pw):
                region = self.slide.read_region((lx, ly), 0, (pw, ph)).convert("RGB")
                arr = np.array(region, dtype=np.uint8)
                tensor = torch.from_numpy(arr).permute(2, 0, 1).contiguous()
                patches.append(tensor)
        return patches

    def __len__(self):
        return len(self.patches)

    def __getitem__(self, idx):
        if self.labels is not None:
            return self.patches[idx], self.labels[idx]
        return self.patches[idx], None
