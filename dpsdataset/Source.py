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
class Record:
    """
    Standardized record object representing one logical item from a Source.
    - metadata: all columns from the strategy's metadata DataFrame row
    - file_path: optional path to file (if applicable)
    - data_type: type hint (e.g., 'image', 'csv', ...)
    - _loader: callable that returns the payload on demand
    """
    metadata: Dict[str, Any]
    file_path: Optional[str] = None
    data_type: Optional[str] = None
    _loader: Optional[Callable[[], Any]] = field(default=None, repr=False)

    def load(self) -> Any:
        """Return the loaded payload using the strategy-provided loader.
        For file-backed records this may return the path or raw bytes/stream depending on loader.
        For CSV rows it may return a dict/Series representing the row."""
        if self._loader:
            return self._loader()
        else:
            return self.metadata

    def open(self, mode: str = "rb"):
        """Convenience to open file_path if present. Returns a file-like object.
        Caller must close the returned object."""
        if not self.file_path:
            raise FileNotFoundError("No file path available for this record.")
        return open(self.file_path, mode)

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

            row = {"file_path": file, "data_type": self.data_type}

            if group_dict:
                row.update(group_dict)
            else:
                row["id"] = match.group(0)

            results.append(row)
            
        df = pd.DataFrame.from_records(results)
        return df
        
    def get_data(self) -> pd.DataFrame:
        return self.__discover_files__()
    
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
        
        
    def get_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.path, sep=self.delimiter, header=0 if self.header else None)
        return df
    
    def get_loader(self, row_dict: Dict[str, Any]) -> Callable[[], Dict[str, Any]]:
        """Return the row dict on demand."""
        return lambda row=row_dict: row

class Source:
    """
    Standardized Source wrapper.
    - self.data: pandas.DataFrame with metadata (keeps backward compatibility)
    - self.records: list[Record] providing lazy access to payloads
    """
    data: Optional[pd.DataFrame]
    records: List[Record]
    
    def __init__(self, source_name: str, type: Optional[DataSourceStrategy]):
        self.source_name = source_name
        self.type = type
        self.records = []
        if type is None:  # intermediate source without data yet
            self.data = None
            logger.debug("Initialized intermediate Source '%s' without data.", self.source_name)
        else:
            self.data = self.type.get_data()
            
            if self.data is None:
                self.records = []
            else:
                records: List[Record] = []
                for row in self.data.to_dict(orient="records"):
                    loader = self.type.get_loader(row)
                    rec = Record(
                        metadata=row,
                        file_path=row.get("file_path"),
                        data_type=row.get("data_type", getattr(self.type, "data_type", None)),
                        _loader=loader
                    )
                    records.append(rec)
                self.records = records

            logger.info("Source '%s' loaded %d records of type '%s'", self.source_name, len(self.records), self.type.type)
        
        
    def get_data(self) -> Optional[pd.DataFrame]:
        """Return metadata DataFrame (backward-compatible)."""
        return self.data

    def list_records(self) -> List[Record]:
        """Return list of Record objects for lazy access."""
        return self.records

    def get_record_by_id(self, id_value: str, id_field: str = "id") -> Optional[Record]:
        """Find a record by id field. Returns first match or None."""
        for r in self.records:
            if id_field in r.metadata and r.metadata[id_field] == id_value:
                return r

            if id_field == "id" and "slide_id" in r.metadata and r.metadata["slide_id"] == id_value:
                return r
        return None
    
    def to_dataframe(self) -> pd.DataFrame:
        """Return the metadata DataFrame, re-built from records if needed."""
        if self.data is not None:
            return self.data
        # if data missing but records present, build DataFrame
        if self.records:
            return pd.DataFrame.from_records([r.metadata for r in self.records])
        return pd.DataFrame()
    
    
if __name__ == "__main__":
    # Example usage
    os.chdir("RIScale")
    
    discovery = FileDiscoveryStrategy(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<slide_id>.+?)(?=\.svs$)")
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<id1>[^.]+)\.(?P<id2>[^.]+)(?:\..*)?\.svs$")
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(.+?)(?=\.svs$)")
    source1 = Source(source_name="source1", type=discovery)
    for rec in source1.list_records():
        print(rec.file_path, rec.load())

    csv_type = CSVFileStrategy(path="./data/labels.csv", delimiter=",", header=True)
    source2 = Source(source_name="source2", type=csv_type)
    for rec in source2.list_records():
        print(rec.file_path, rec.load())

