import argparse
import os
import queue
import sys
import logging
import yaml
from DPSPipeline import DPSPipeline
from dpsstep.SVSDataLoaderStep import SVSDataLoaderStep
from dpsstep.ExampleDPSStep import ExampleDPSStep
import pandas as pd

logger = logging.getLogger(__name__)

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Validate pipeline arguments")
    parser.add_argument("-m", "--manifest", required=True, help="Manifest file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args(argv)

    if not os.path.exists(args.manifest):
        parser.error(f"Manifest path not found: {args.manifest}")
    return args

class DataPreparationForExploitationService:
    """
    The Data Preparation for Exploitation Service (DPS) is a user-invoked service that prepares datasets
    on the DEP for downstream use. After the data orchestration service has copied original RI datasets
    onto the platform, users launch the DPS to apply the necessary pre-processing steps. Its role is to
    translate the heterogeneous outputs of participating RIs, ranging from gigapixel whole-slide images
    (WSI) and multidimensional climate cubes to long-term radar time series of atmospheric parameters,
    into data objects whose formats, metadata, and directory structure meet the input requirements of
    the algorithms available on the DEP, while maintaining a consistent, platform-wide convention. This
    ensures that data ingestion is harmonised across domains and that every dataset can be used
    directly in workflows without further ad-hoc manipulation.
    """
    def __init__(self, manifest_path:str):
        self.manifest_path:str = manifest_path
        self.pipeline: DPSPipeline = DPSPipeline()
        self.__parse_manifest__()

    def __parse_manifest__(self):
        logger.info("Parsing manifest: %s", self.manifest_path)
        with open(self.manifest_path, 'r') as f:
            manifest = yaml.safe_load(f) 
            received = manifest.get('received_files', {})
            file_info = {}
            if isinstance(received, dict):
                file_info = received
            elif isinstance(received, list):
                for item in received:
                    if isinstance(item, dict):
                        file_info.update(item)
                    else:
                        logger.warning("Unexpected item in received_files list: %r", item)

            self.data_path = file_info.get('data_folder', '')
            self.labels_file = file_info.get('labels_file', '')

            if self.labels_file:
                self.labels = pd.read_csv(self.labels_file, sep=',')
                try:
                    self.labels = pd.read_csv(self.labels_file, sep=',')
                except Exception:
                    logger.exception("Failed to read labels file: %s", self.labels_file)
                    self.labels = None

            steps = manifest.get('dps_steps', file_info.get('dps_steps', []))
            for step_name in steps:
                if step_name == "SVSDataLoaderStep":
                    step = SVSDataLoaderStep(recursive=False, labels=self.labels)
                    self.pipeline.add_step(step)
                elif step_name == "ExampleDPSStep":
                    step = ExampleDPSStep()
                    self.pipeline.add_step(step)
                else:
                    logger.warning("Unknown DPS step: %s", step_name)


    def run(self):
        logger.info("Running DPS on manifest: %s", self.manifest_path)
        
        data_path = self.data_path
    
        processed_data = self.pipeline.execute(data_path)
        logger.info("Data preparation complete.")
        return processed_data


if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
        logger.setLevel(logging.INFO)
    else:
        logging.disable(logging.CRITICAL)
        logger.disabled = True
        
    logger.info("Arguments: %s", args)
    dps = DataPreparationForExploitationService(args.manifest)
    dps.run()
    

