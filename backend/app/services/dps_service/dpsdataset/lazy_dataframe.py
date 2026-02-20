from typing import Callable
import pandas as pd

class LazyRow:
    def __init__(self, row, field_loaders:dict[str, callable]):
        self._row = row
        self._field_loaders = field_loaders
        self._cache: dict[str, object] = {}
        self.index = row.index
        
    def __getitem__(self, key: str):
        if key in self._cache:
            return self._cache[key]
        
        if key in self._field_loaders:
            loader = self._field_loaders[key]
        else:
            loader = None
        
        try:
            if loader == None:
                value = self._row[key]
            else:
                value = loader(self._row[key])
            
            self._cache[key] = value
                
            return value
        except KeyError:
            raise KeyError(f"Key {key} not found in LazyRow.")
    
    def __repr__(self):
        return self._row.__repr__()
    
    def to_dict(self):
        result = {}
        for col in self._row.index:
            result[col] = self[col]
        return result
    
    def __len__(self):
        return len(self._row)
    


class LazySeries:
    def __init__(self, series: pd.Series, col:str, loader:Callable):
        self._series = series
        self._col = col
        self._loader = loader

    def __getitem__(self, index):
        if isinstance(index, int):
            value = self._series.iloc[index]
            if self._loader is not None:
                value = self._loader(value)
            return value
        else:
            return self._series.__getitem__(index)
        
        
    def __repr__(self):
        return self._series.__repr__()
    
    def to_list(self):
        result = []
        for i in range(len(self._series)):
            result.append(self[i])
        return result
    
    def __len__(self):
        return len(self._series)
    
    def __iter__(self):
        for i in range(len(self._series)):
            yield self[i]

class LazyDataFrame():
    """
    Custom DataFrame that supports lazy loading of fields using provided loaders.
    """
    
    _dataframe: pd.DataFrame = None
    _field_loaders: dict[str, callable] = {}
    
    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False, field_loaders: dict[str, callable] = {}):
        self._dataframe = pd.DataFrame(data, index=index, columns=columns, dtype=dtype, copy=copy)
        self._field_loaders = field_loaders
        self.columns = self._dataframe.columns
        
    def __getitem__(self, key):
        result = self._dataframe.__getitem__(key)
        
        if isinstance(result, pd.Series):
            result = LazySeries(result, key, self._field_loaders.get(key, None))
        elif isinstance(result, pd.DataFrame):
            result = LazyDataFrame(result, field_loaders=self._field_loaders)
        else:
            result = LazyRow(result, self._field_loaders)
        
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
    
    def __len__(self):
        return len(self._dataframe)
    
    def to_pandas(self):
        return self._dataframe.copy()
    
    def to_dict(self, orient='dict'):
        result = {}
        for col in self._dataframe.columns:
            series = self[col]
            result[col] = series.to_list()
        return result
    
    def dropna(self, **kwargs):
        """Drop rows with NaN values, preserving field loaders."""
        cleaned = self._dataframe.dropna(**kwargs)
        return LazyDataFrame(cleaned, field_loaders=self._field_loaders)

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
            for name, loader in right_loaders.items():
                if name in merged_field_loaders:
                    sx, sy = suffixes
                    merged_field_loaders[f"{name}{sx}"] = merged_field_loaders.pop(name)
                    merged_field_loaders[f"{name}{sy}"] = loader
                else:
                    merged_field_loaders[name] = loader
        
        return LazyDataFrame(merged_df, field_loaders=merged_field_loaders)