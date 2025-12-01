import pandas as pd
import glob
import os
import re
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from traitlets import Type
logger = logging.getLogger(__name__)

@dataclass
class DataWithMetadata:
    """
    Helper class to represent a DataFrame element with associated metadata.
    - data_type: type of data in the column (e.g., 'int', 'float', 'string', 'image', etc.)
    - loaded: whether the data is loaded in memory
    - loaded_data: the actual data if loaded
    - load_path: path to load the data from if not loaded
    - loader: callable to load the data from load_path
    """
    def __init__(self, data_type: str, loaded_data: Optional[pd.Series] = None, load_path: Optional[str] = None, loader: Optional[Callable] = None):
        
        if loaded_data is not None:
            self.loaded = True
            self.loaded_data = loaded_data
        else:
            self.loaded = False
            self.loaded_data = None
            
        if not self.loaded_data and (load_path  is None and loader is None):
            raise ValueError("Either loaded_data or load_path/loader must be provided.")
        
        self.data_type = data_type
        self.load_path = load_path
        self.loader = loader
        
    def __repr__(self):
        return f"Data(data_type={self.data_type}, loaded={self.loaded})"
    
    def __str__(self):
        return self.__repr__()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "column_name": self.column_name,
            "data_type": self.data_type,
            "loaded": self.loaded,
            "load_path": self.load_path,
            "loaded_data": self.loaded_data
        }
        
    def load_data(self):
        """Load the data from load_path if not already loaded."""
        if self.loaded:
            return self.loaded_data
        if self.loader:
            self.loaded_data = self.loader(self.load_path)
            self.loaded = True
        else:
            raise ValueError("No loader function provided to load data.") # should never happen
        
        return self.loaded_data
    
    def is_loaded(self) -> bool:
        """Check if the data is loaded."""
        return self.loaded
    
    def unload_data(self):
        """Unload the data to free memory."""
        if self.loaded_data is not None:
            self.loaded_data = None
            self.loaded = False
        else:
            logger.warning("Data is already unloaded.")
            
    def get_data(self) -> Optional[pd.Series]:
        """Get the loaded data, or try to load if not loaded."""
        if not self.loaded:
            return self.load_data()
        
        return self.loaded_data
    

class LazyRow:
    def __init__(self, row, field_loaders:dict[str, callable]):
        self._row = row
        self._field_loaders = field_loaders
        self._cache: dict[str, object] = {}
        
    def __getitem__(self, key: str):
        if key in self._cache:
            return self._cache[key]
        
        if key in self._field_loaders:
            loader = self._field_loaders[key]
            if loader == None:
                value = self._row[key]
            else:
                value = loader(self._row)
                
            self._cache[key] = value
            
            return value
        
        raise KeyError(f"Key {key} not found in LazyRow.")


class Dataframe(pd.DataFrame):
    """
    Custom DataFrame that supports lazy loading of fields using provided loaders.
    """
    def __init__(self, data, index, columns, dtype, copy, field_loaders: dict[str, callable]):
        """Initialize the Dataframe with lazy loading capabilities.
        
        Args:
            data: ndarray (structured or homogeneous), Iterable, dict, or DataFrame
                Dict can contain Series, arrays, constants, dataclass or list-like objects. If data is a dict, column order follows insertion-order. If a dict contains Series which have an index defined, it is aligned by its index. This alignment also occurs if data is a Series or a DataFrame itself. Alignment is done on Series/DataFrame inputs. If data is a list of dicts, column order follows insertion-order.

            index: Index or array-like
                Index to use for resulting frame. Will default to RangeIndex if no indexing information part of input data and no index provided.

            columns: Index or array-like
                Column labels to use for resulting frame when data does not have them, defaulting to RangeIndex(0, 1, 2, ..., n). If data contains column labels, will perform column selection instead.

            dtype: dtype, default None
                Data type to force. Only a single dtype is allowed. If None, infer.

            copy: bool or None, default None
                Copy data from inputs. For dict data, the default of None behaves like copy=True. For DataFrame or 2d ndarray input, the default of None behaves like copy=False. If data is a dict containing one or more Series (possibly of different dtypes), copy=False will ensure that these inputs are not copied.

            field_loaders: dict[str, callable]
                Dictionary mapping column names to loader functions for lazy loading.
        """
        super().__init__(data, index=index, columns=columns, dtype=dtype, copy=copy)
        self._field_loaders = field_loaders
        
        
    def __getitem__(self, key: str):
        row = self.iloc[key]
        return LazyRow(row, self._field_loaders)
    
        
class DataSourceStrategy():
    """Base class for data source strategies."""
    
    def __init__(self, type:str):
        """Initialize the DataSourceStrategy.
        Args:
            type (str): Type of the data source strategy.
        """
        self.type = type


    def get_data(self) -> pd.DataFrame:
        """return tuple of (path, data_type, id | None)"""
        raise NotImplementedError("Subclasses should implement this method.")
    
    def get_loader(self, row_dict: Dict[str, Any]) -> Callable[[], Any]:
        """Return a callable that lazily loads the payload for a row.
        Default implementation returns the row metadata."""
        return lambda row=row_dict: row

    
class FileDiscoveryStrategy(DataSourceStrategy):
    """
    Strategy to discover files in a directory based on a pattern.
    """
    
    def __init__(self, path:str, include:str="*.svs", recursive:bool=False, id_pattern:str="^(?P<slide_id>[^.]+)", data_type:str="image"):
        """
        Initialize the FileDiscoveryStrategy.
        Args:
            path (str): Directory path to search for files.
            include (str): Pattern for files to be included e.g. "*.svs".
            recursive (bool): Whether to search recursively.
            id_pattern (str): Regex pattern to extract IDs from filename. \
            Regex groups will be used as columns, e.g. "(?P<slide_id>[^.]+)"\
            will create a 'slide_id' column, where every value is extracted until\
            the first "." dot-character appears. Multiple columens are possible based one the filename.\
            If no named groups are used, a single 'id' column will be created.
            data_type (str): Type of data being discovered. 
        """
        super().__init__(type="discovery")
        self.path = path
        self.include = include
        self.recursive = recursive
        self.id_pattern = id_pattern
        self.data_type = data_type
        
        
    def __discover_files__(self):
        pattern = "**/" + self.include if self.recursive else self.include
        search_path = os.path.join(self.path, pattern)
        files: list[str] = glob.glob(search_path, recursive=self.recursive)
        regex = re.compile(self.id_pattern)

        results = []
        for file in files:
            name = os.path.basename(file)
            match = regex.match(name)
            if not match:
                logger.warning("Filename %s does not match pattern %s", name, self.id_pattern)
                continue
            group_dict = match.groupdict()

            element = DataWithMetadata(data_type=self.data_type, load_path=file, loader=lambda p=file: p) # TODO: change loader to actual data loader
            row = {}
            if group_dict:
                row.update(group_dict)
            else:
                row["id"] = match.group(0)
                
            row["values"] = element
            
            results.append(row)
        
        df = pd.DataFrame(results)
        return df
    
        
    def get_data(self) -> pd.DataFrame:
        return self.__discover_files__().to_dict(orient="records")
    
    
    def get_loader(self, row_dict: Dict[str, Any]) -> Callable[[], str]:
        """Loader returns the file path by default (lazy)."""
        path = row_dict.get("file_path")
        return lambda p=path: p


class CSVFileStrategy(DataSourceStrategy):
    """
    Strategy to load data from a CSV file.
    """
    
    def __init__(self, path:str, delimiter:str=",", header:bool=True):
        """
        Initialize the CSVFileStrategy.
        Args:
            path (str): Path to the CSV file.
            delimiter (str): Delimiter used in the CSV file.
            header (bool): Whether the CSV file has a header row.
        """
        super().__init__(type="csv_file")
        self.path = path
        self.delimiter = delimiter
        self.header = header
        self.data_type = "csv"
        
        
    def get_data(self) -> List[Dict[str, Any]]:
        df = pd.read_csv(self.path, sep=self.delimiter, header=0 if self.header else None)
        return df.to_dict(orient="records")
    
    def get_loader(self, row_dict: Dict[str, Any]) -> Callable[[], Dict[str, Any]]:
        """Return the row dict on demand."""
        return lambda row=row_dict: row


class Source:
    def __init__(self, source_name: str, data_source_strategy: Optional[DataSourceStrategy]):
        """
        Initialize the Source.
        Args:
            source_name (str): Name of the data source.
            data_source_strategy (DataSourceStrategy): Strategy to load data from the source.
        """
        self.source_name = source_name
        self.data_source_strategy = data_source_strategy
        
        self._data: Optional[pd.DataFrame] = data_source_strategy.get_data() if data_source_strategy else None
        
        
    def get_data(self) -> Optional[pd.DataFrame]:
        """Get the data from the source."""
        return self._data
        

if __name__ == "__main__":
    # Example usage
    os.chdir("RIScale")
    
    discovery = FileDiscoveryStrategy(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<slide_id>.+?)(?=\.svs$)")
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<id1>[^.]+)\.(?P<id2>[^.]+)(?:\..*)?\.svs$")
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(.+?)(?=\.svs$)")
    source1 = Source(source_name="source1", data_source_strategy=discovery)
    for rec in source1.get_data():
        print(rec)
        
    csv_type = CSVFileStrategy(path="./data/labels.csv", delimiter=",", header=True)
    source2 = Source(source_name="source2", data_source_strategy=csv_type)
    for rec in source2.get_data():
        print(rec)

