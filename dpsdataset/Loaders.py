from typing import Generator
from PIL.Image import Image
import pandas as __pd
from logging import getLogger as __getLogger
import openslide

__logger = __getLogger(__name__)

__loader_register:dict[str, callable] = {}

def getLoader(type):
    """
    Return corresponding loader function based on the first argument:
    #### type:
    
        "wsi" - Whole Slide Image loader
        "csv" - CSV file loader
    """
    
    return __loader_register.get(type, __example_loader)

def register(type):
    """
    Can be used as:
      @register("csv")
      def loader(path): ...
    """
    def decorator(func):
        __loader_register[type] = func
        return func
    return decorator

"""
Add Loaders and register them here:
"""
@register("example")
def __example_loader(path):
    __logger.error(f"Using example Loader for path: {path}")
    return f"<LoadedObject: {path}>"

@register("wsi")
def __wsi_loader(path) -> Generator[Image, None, None]:
    __logger.debug(f"Loading WSI from path: {path}")
    try:
        slide = openslide.OpenSlide(path)
        width, height = slide.dimensions
        patch_w, patch_h = 512, 512

        for y in range(0, height, patch_h):
            for x in range(0, width, patch_w):
                size_x = min(patch_w, width - x)
                size_y = min(patch_h, height - y)
                __logger.debug(f"Reading region x={x} y={y} size=({size_x},{size_y}) level=0")
                region = slide.read_region((x, y), 0, (size_x, size_y)).convert("RGB")
                yield region
        
        slide.close()
    finally:
        try:
            slide.close()
        except Exception:
            __logger.debug("Failed to close slide", exc_info=True)

@register("csv")
def __csv_loader(path):
    __logger.debug(f"Loading CSV from path: {path}")
    return __pd.read_csv(path)

