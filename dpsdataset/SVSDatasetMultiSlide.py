from typing import List, Tuple, Optional, Callable
import random
import openslide
import torch
from torch.utils.data import Dataset
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SlidePatchExtractor:
    """Facade to read patches from an OpenSlide slide file."""

    def __init__(self, slide_path: str, patch_size: Tuple[int, int] = (512, 512)):
        self.slide_path = slide_path
        self.patch_size = tuple(patch_size)
        self.slide = openslide.OpenSlide(slide_path)
        self.level0_w, self.level0_h = self.slide.level_dimensions[0]


    def grid_coords(self) -> List[Tuple[int, int]]:
        pw, ph = self.patch_size
        coords = []
        for y in range(0, self.level0_h, ph):
            for x in range(0, self.level0_w, pw):
                coords.append((x, y))
        return coords


    def read_patch(self, coord: Tuple[int, int], level:int = 0) -> torch.Tensor:
        x, y = coord
        pw, ph = self.patch_size
        region = self.slide.read_region((int(x), int(y)), level, (pw, ph)).convert("RGB")
        arr = np.array(region, dtype=np.uint8)
        tensor = torch.from_numpy(arr).permute(2, 0, 1).contiguous()
        return tensor


class SVSDatasetMultiSlide(Dataset):
    def __init__(self, slides: List[dict], patch_size: Tuple[int, int] = (512, 512), patches_per_slide: int | None = None):
        """
        Dataset to load patches from multiple SVS slides.
        slides: List of dicts with keys:
            - "slide_path": path to the SVS file
            - "label": optional label for the slide
        patch_size: Size of patches to extract
        patches_per_slide: Number of patches to sample per slide. If None, use all patches.
        """
        self.slides = slides
        self.patch_size = patch_size
        self.patches_per_slide = patches_per_slide

        self._coords_map = [] 
        for s in self.slides:
            extractor = SlidePatchExtractor(s["slide_path"], patch_size=self.patch_size)
            coords = extractor.grid_coords()
            self._coords_map.append(coords)
            
        random.seed(42)
        np.random.seed(42)


    def __len__(self):
        return len(self.slides)


    def __getitem__(self, idx: int):
        slide_entry = self.slides[idx]
        slide_path = slide_entry["slide_path"]
        label = slide_entry.get("label", None)

        extractor = SlidePatchExtractor(slide_path, patch_size=self.patch_size)
        coords = self._coords_map[idx]
        
        if self.patches_per_slide is None:
            k = len(coords)
        else:
            k = self.patches_per_slide
            
        logger.info(f"Sampling {k} patches from slide {slide_path} with total {len(coords)} patches available.")

        if k <= len(coords):
            sampled = random.sample(coords, k)
        else:
            logger.warning(f"Requested {k} patches, but only {len(coords)} available. Sampling all.")
            sampled = coords

        patches = []
        for c in sampled:
            p = extractor.read_patch(c)
            patches.append(p)

        patches_tensor = torch.stack(patches, dim=0)

        return patches_tensor, label
    

