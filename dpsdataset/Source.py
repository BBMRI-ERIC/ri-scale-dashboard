import pandas as pd
import glob
import os
import re
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from traitlets import Type

from .Loaders import getLoader
from .LazyDataframe import LazyDataFrame

logger = logging.getLogger(__name__)
    
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
    
    
class FileDiscoveryStrategy(DataSourceStrategy):
    """
    Strategy to discover files in a directory based on a pattern.
    """
    
    def __init__(self, path:str, include:str="*.svs", recursive:bool=False, id_pattern:str="^(?P<slide_id>[^.]+)", loader:Callable=None, column_name:str="path"):
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
        self.loader = loader
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

            element = file
            row = {}
            if group_dict:
                row.update(group_dict)
            else:
                row["id"] = match.group(0)
                
            row[self.column_name] = element
            
            results.append(row)
        
        df = LazyDataFrame(results, field_loaders={self.column_name: self.loader})
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
    #os.chdir("RIScale")
    loader = getLoader("wsi")
    
    discovery = FileDiscoveryStrategy(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<slide_id>.+?)(?=\.svs$)", loader=loader)
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<id1>[^.]+)\.(?P<id2>[^.]+)(?:\..*)?\.svs$", loader=loader)
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(.+?)(?=\.svs$)", loader=loader)
    
    source1 = Source(source_name="source1", data_source_strategy=discovery)
    
    print(source1.get_data())
    
    for rec in source1.get_data()["path"]:
        print(rec)
        
    csv_type = CSVFileStrategy(path="./data/labels.csv", delimiter=",", header=True)
    source2 = Source(source_name="source2", data_source_strategy=csv_type)
    
    for rec in source2.get_data().iterrows():
        print(rec)
        for x in rec:
            print(x)
        print("")

    merged = source1.get_data()
    merged = merged.merge(source2.get_data(), left_on="slide_id", right_on="slide_id", how="left")
    
    print(merged)
    
    for row in merged.itertuples():
        print(row)
        
    # access LazyRow
    print("access LazyRow:\n", merged["path"], "\n")
    
    #lazy_loading
    print("lazy loaded:\n", merged["path"][1], "\n")
    for patch in merged["path"][1]:
        print(patch)
        
    #non lazy access
    print("non lazy loaded:\n", merged["slide_id"][1], "\n")