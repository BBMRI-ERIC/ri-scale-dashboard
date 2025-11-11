"""
SVS loading step for RISCale DPS pipeline.

This step looks for SVS files in a provided directory and updates the input
`data` dict with the discovered file paths under the key `svs_paths`.
"""
import os
import glob
import logging
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any

from .DataLoaderStep import DataLoaderStep
from dpsdataset.SVSDatasetMultiSlide import SVSDatasetMultiSlide



logger = logging.getLogger(__name__)


class SVSDataLoaderStep(DataLoaderStep):

    def __init__(self, name: str = "SVS Loader", recursive: bool = False, labels: pd.DataFrame | None = None):
        super().__init__(name)
        self.recursive = recursive
        self.extensions = [".svs"]
        self.labels = labels


    def _find_files(self, dirpath: str) -> List[str]:
        if not os.path.isdir(dirpath):
            logger.warning(f"{self.name}: Provided path {dirpath} is not a directory.")
            return []
        matches: List[str] = []
        pattern = "**/*" if self.recursive else "*"
        for root, _, files in os.walk(dirpath):
            if not self.recursive and root != dirpath:
                break
            for f in files:
                _, ext = os.path.splitext(f)
                if ext.lower() in [e.lower() for e in self.extensions]:
                    matches.append(os.path.join(root, f))
        matches = sorted(set(matches))
        return matches
    
    
    def _match_labels(self, files: List[str]) -> List[Any]:
        if self.labels is None:
            return [None] * len(files)

        labels_map = {}
        if 'slide_id' in self.labels.columns and 'label' in self.labels.columns:
            labels_map = dict(zip(
            self.labels['slide_id'].astype(str).str.strip(),
            self.labels['label'].tolist()
            ))
        else:

            first_col = self.labels.columns[0]
            labels_map = dict(zip(
            self.labels.index.astype(str).str.strip(),
            self.labels[first_col].tolist()
            ))

        matched_labels = []
        for f in files:
            filename = os.path.basename(f).strip()

            label = labels_map.get(filename, None)

            if label is None:
                name_no_ext = os.path.splitext(filename)[0]
                label = labels_map.get(name_no_ext, None)
            if label is None:
                logger.warning(f"{self.name}: No label found for file {filename}.")
            matched_labels.append(label)
        return matched_labels


    def execute(self, data_path: str | Path) -> SVSDatasetMultiSlide:
        dirpath = str(data_path)
    
        files = self._find_files(dirpath)
        logger.info(f"{self.name}: Found {len(files)} file(s) matching extensions {self.extensions} in {dirpath}")

        labels = self._match_labels(files)

        dataset = SVSDatasetMultiSlide(
            slides=[{"slide_path": f, "label": l} for f, l in zip(files, labels)],
            patch_size=(1024, 1024)
        )
        
        logger.info(f"{self.name}: Created SVSDatasetMultiSlide with {len(dataset)} patches from {len(files)} slides.")
        
        return dataset

