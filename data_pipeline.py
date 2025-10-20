import argparse
import os
import queue
import sys
import logging

logger = logging.getLogger(__name__)

print("test")

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Validate pipeline arguments")
    parser.add_argument("-m", "--manifest", required=True, help="Manifest file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args(argv)

    if not os.path.exists(args.manifest):
        parser.error(f"Manifest path not found: {args.manifest}")

    return args


class DPSStep:
    """
    Base class for data preparation steps.
    Each step should implement the `execute` method.
    """
    def __init__(self, name:str):
        self.name = name

    def execute(self, data: any) -> any:
        """
        Execute the data preparation step.
        Input:
            data: The input data to be processed.
        Output:
            The processed data.
        """
        raise NotImplementedError("Each step must implement the execute method.")
    


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
        self.pipeline: queue.Queue[DPSStep] = queue.Queue()

    def parse_manifest(self):
        logger.info("Parsing manifest: %s", self.manifest_path)


    def run(self):
        logger.info("Running DPS on manifest: %s", self.manifest_path)
        
        data = None # TODO: Load initial data based on manifest
        for step in self.pipeline.queue:
            logger.info("Executing step: %s", step.name)
            data = step.execute(data)
        
        logger.info("Data preparation complete.")


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

