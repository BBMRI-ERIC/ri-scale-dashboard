import pandas as pd
import glob
import os
import re
import logging
logger = logging.getLogger(__name__)

class DataSourceStrategy():
    def __init__(self, type:str):
        self.type = type


    def get_data(self) -> pd.DataFrame:
        """return tuple of (path, data_type, id | None)"""
        raise NotImplementedError("Subclasses should implement this method.")

    
class FileDiscoveryStrategy(DataSourceStrategy):
    def __init__(self, path:str, include:str="*.svs", recursive:bool=False, id_pattern:str="^(?P<slide_id>[^.]+)", data_type:str="image"):
        super().__init__(type="discovery")
        self.path = path
        self.include = include
        self.recursive = recursive
        self.id_pattern = id_pattern
        self.data_type = data_type
        
        
    def discover_files(self):
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
        return self.discover_files()


class CSVFileStrategy(DataSourceStrategy):
    def __init__(self, path:str, key_field:str="slide_id", delimiter:str=",", header:bool=True):
        super().__init__(type="csv_file")
        self.path = path
        self.key_field = key_field
        self.delimiter = delimiter
        self.header = header
        self.data_type = "csv"
        
        
    def get_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.path, sep=self.delimiter, header=0 if self.header else None)
        return df

class Source:
    def __init__(self, source_name:str, type:DataSourceStrategy):
        self.source_name = source_name
        self.type = type
        self.data: pd.DataFrame = self.type.get_data()
        logger.info("Source '%s' loaded %d files of type '%s'", self.source_name, len(self.data), self.type.type)
        
        
    def get_data(self) -> pd.DataFrame:
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

