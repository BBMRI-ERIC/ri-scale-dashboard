import pandas as pd
import glob
import os
import re
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from traitlets import Type
logger = logging.getLogger(__name__)
    

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
    
    def __repr__(self):
        return self._row.__repr__()


class LazySeries:
    def __init__(self, series: pd.Series, col:str, loader:Callable):
        self._series = series
        self._col = col
        self._loader = loader

    def __getitem__(self, index):
        if isinstance(index, int):
            value = self._series.iloc[index]
            value = self._loader(value)
            return value
        else:
            return self._series.__getitem__(index)
        
        
    def __repr__(self):
        return self._series.__repr__()

class LazyDataFrame():
    """
    Custom DataFrame that supports lazy loading of fields using provided loaders.
    """
    
    _dataframe: pd.DataFrame = None
    _field_loaders: dict[str, callable] = {}
    
    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False, field_loaders: dict[str, callable] = {}):
        self._dataframe = pd.DataFrame(data, index=index, columns=columns, dtype=dtype, copy=copy)
        self._field_loaders = field_loaders
        
    def __getitem__(self, key):
        result = self._dataframe.__getitem__(key)
        
        if isinstance(result, pd.Series):
            result = LazySeries(result, key, self._field_loaders[key])
        elif isinstance(result, pd.DataFrame):
            result = LazyDataFrame(result, field_loaders=self._field_loaders)
        else:
            result = LazyRow(result, self._field_loaders)
        
        logger.debug(f"Accessing key {key} in LazyDataFrame")
        return result
    
    def iterrows(self):
        for index, row in self._dataframe.iterrows():
            yield index, LazyRow(row, self._field_loaders)
            
    def itertuples(self):
        for row in self._dataframe.itertuples():
            yield row
    
    def __iter__(self):
        return iter(self._dataframe)
    
    
    def __repr__(self):
        return self._dataframe.__repr__()
    
    
    def merge(self, right, how="inner", on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'), copy=True, indicator=False, validate=None):
        """
        Merge two DataFrames and combine field loaders from LazyDataFrame inputs.
        """
        
        left_df = self._dataframe
        right_df = right._dataframe if isinstance(right, LazyDataFrame) else right
        
        merged_df = left_df.merge(
            right_df,
            how=how,
            on=on,
            left_on=left_on,
            right_on=right_on,
            left_index=left_index,
            right_index=right_index,
            sort=sort,
            suffixes=suffixes,
            copy=copy,
            indicator=indicator,
            validate=validate
        )
        
        merged_field_loaders = dict(self._field_loaders or {})
        right_loaders = getattr(right, "_field_loaders", None)
        if right_loaders:
            merged_field_loaders.update(right_loaders)
        
        return LazyDataFrame(merged_df, field_loaders=merged_field_loaders)
    
    
class DataSourceStrategy():
    """Base class for data source strategies."""
    
    def __init__(self, type:str):
        """Initialize the DataSourceStrategy.
        Args:
            type (str): Type of the data source strategy.
        """
        self.type = type


    def get_data(self) -> LazyDataFrame:
        """return tuple of (path, data_type, id | None)"""
        raise NotImplementedError("Subclasses should implement this method.")
    

    
def example_loader(path):
    print(f"Loading data from path: {path}")
    return f"<LoadedObject: {path}>"

    
class FileDiscoveryStrategy(DataSourceStrategy):
    """
    Strategy to discover files in a directory based on a pattern.
    """
    
    def __init__(self, path:str, include:str="*.svs", recursive:bool=False, id_pattern:str="^(?P<slide_id>[^.]+)", data_type:str="image", column_name:str="path"):
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
        self.column_name = column_name
        
        
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

            element = file #DataWithMetadata(data_type=self.data_type, load_path=file, loader=lambda p=file: p) # TODO: change loader to actual data loader
            row = {}
            if group_dict:
                row.update(group_dict)
            else:
                row["id"] = match.group(0)
                
            row[self.column_name] = element
            
            results.append(row)
        
        df = LazyDataFrame(results, field_loaders={self.column_name: example_loader})  # TODO: change loader to actual data loader
        return df
    
        
    def get_data(self) -> LazyDataFrame:
        return self.__discover_files__()
    


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
        
        
    def get_data(self) -> LazyDataFrame:
        df = pd.read_csv(self.path, sep=self.delimiter, header=0 if self.header else None)
        return LazyDataFrame(df)
    


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
        
        
    def get_data(self) -> Optional[LazyDataFrame]:
        """Get the data from the source."""
        return self._data
        

if __name__ == "__main__":
    # Example usage
    os.chdir("RIScale")
    
    discovery = FileDiscoveryStrategy(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<slide_id>.+?)(?=\.svs$)")
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<id1>[^.]+)\.(?P<id2>[^.]+)(?:\..*)?\.svs$")
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(.+?)(?=\.svs$)")
    source1 = Source(source_name="source1", data_source_strategy=discovery)
    
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    print("\n", df["a"][1], "\n")
    # for rec in df["a"]:
    #     print(rec)
        
    
    # print(source1.get_data())
    
    # for rec in source1.get_data()["path"]:
    #     print(rec)
        
    # print(source1.get_data()._field_loaders)
        
    csv_type = CSVFileStrategy(path="./data/labels.csv", delimiter=",", header=True)
    source2 = Source(source_name="source2", data_source_strategy=csv_type)
    #for rec in source2.get_data().iterrows():
    #   print(rec)
        # for x in rec:
        #     print(x)

    merged = source1.get_data()
    merged = merged.merge(source2.get_data(), left_on="slide_id", right_on="slide_id", how="left")
    
    print(merged)
    
    for row in merged.itertuples():
        print(row)
        
    # access LazyRow
    print("\n", merged["path"], "\n")
    
    #lazy_loading
    print("\n", merged["path"][1], "\n")