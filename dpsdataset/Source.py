import pandas as pd
import glob
import os
import re
import logging

from traitlets import Type
logger = logging.getLogger(__name__)

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

class Source:
    def __init__(self, source_name:str, type:DataSourceStrategy):
        """Data source for DPS pipeline.
        Args:
            source_name (str): Name of the data source.
            type (DataSourceStrategy): Strategy to load the data. None for intermediate outputs that are pupulated later..
        """
        self.source_name = source_name
        self.type = type
        if type is None: # intermediate source without data yet
            self.data = None
        else:
            self.data: pd.DataFrame = self.type.get_data()
            logger.info("Source '%s' loaded %d files of type '%s'", self.source_name, len(self.data), self.type.type)
        
        
    def get_data(self) -> pd.DataFrame:
        """
        Get the data from the source.
        Returns:
            pandas.DataFrame: The data contained in the source.
        """
        return self.data
    
    
if __name__ == "__main__":
    # Example usage
    os.chdir("RIScale")
    
    discovery = FileDiscoveryStrategy(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<slide_id>.+?)(?=\.svs$)")
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(?P<id1>[^.]+)\.(?P<id2>[^.]+)(?:\..*)?\.svs$")
    #discovery = DiscoveryType(path="./data/", include="*.svs", recursive=False, id_pattern=r"^(.+?)(?=\.svs$)")
    source1 = Source(source_name="source1", type=discovery)
    df1 = source1.get_data()
    print(df1)

    csv_type = CSVFileStrategy(path="./data/labels.csv", key_field="id", delimiter=",", header=True)
    source2 = Source(source_name="source2", type=csv_type)
    df2 = source2.get_data()
    print(df2)

