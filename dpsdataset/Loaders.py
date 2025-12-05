import pandas as __pd
from logging import getLogger as __getLogger

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
      def loader(...): ...
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
def __wsi_loader(path):
    __logger.debug(f"Loading WSI from path: {path}")
    return f"<WSIObject (Not implemented): {path}>"

@register("csv")
def __csv_loader(path):
    __logger.debug(f"Loading CSV from path: {path}")
    return __pd.read_csv(path)

