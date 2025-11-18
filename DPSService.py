"""
Data Preparation for Exploitation Service (DPS) module.
USAGE EXAMPLE:
    python DPSService.py -m ./example_manifest.yaml -v
"""

import argparse
import os
import queue
import sys
import logging
import yaml
from DPSPipeline import DPSPipeline
from dpsstep.ExampleDPSStep import ExampleDPSStep
from dpsstep.JoinStep import JoinStep
import pandas as pd
from dpsdataset.Source import DataSourceStrategy, FileDiscoveryStrategy, CSVFileStrategy, Source

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
        """
        Initialize the DPS with a manifest file.
        Args:
            manifest_path (str): Path to the manifest YAML file defining sources and steps.
        """
        self.manifest_path:str = manifest_path
        self.pipeline: DPSPipeline = DPSPipeline()
        self.__parse_manifest__()

    def __parse_manifest__(self):
        """
        Parse the manifest YAML file to initialize sources and steps.
        """
        
        logger.info("Parsing manifest: %s", self.manifest_path)
        with open(self.manifest_path, 'r') as f:
            manifest = yaml.safe_load(f) 
            manifest_id = manifest.get('manifest_id', {})
            created_by = manifest.get('created_by', '')
            created_at = manifest.get('created_at', '')
            logger.info("Manifest ID: %s, created by: %s at %s",
                        manifest_id, created_by, created_at)
            
            defined_sources = manifest.get('sources', [])
            self.sources: dict[str, Source] = {}
            
            for defined_source in defined_sources:
                match defined_source.get('type', ''):
                    case 'csv_file':
                        csv_source = Source(
                            source_name=defined_source.get('source_name', 'csv_source'),
                            type=CSVFileStrategy(
                                path=defined_source.get('path', ''),
                                key_field=defined_source.get('params', {}).get('key_field', 'slide_id'),
                                delimiter=defined_source.get('params', {}).get('delimiter', ','),
                                header=defined_source.get('params', {}).get('header', True)
                            )
                        )
                        self.sources[csv_source.source_name] = csv_source                   
                        
                    case 'discovery':
                        discovery_source = Source(
                            source_name=defined_source.get('source_name', 'discovery_source'),
                            type=FileDiscoveryStrategy(
                                path=defined_source.get('path', ''),
                                include=defined_source.get('params', {}).get('include', '*.svs'),
                                recursive=defined_source.get('params', {}).get('recursive', False),
                                id_pattern=defined_source.get('params', {}).get('id_pattern', '^(?P<slide_id>[^.]+)'),
                                data_type=defined_source.get('params', {}).get('data_type', 'image')
                            )
                        )
                        self.sources[discovery_source.source_name] = discovery_source
                        
                    case 'step_output':
                        raise NotImplementedError("Source type 'step_output' is not implemented yet.")
                    case _:
                        logger.error("Unknown source type: %s", defined_source.get('type', ''))
        

            steps = manifest.get('dps_steps', manifest.get('job_steps', []))
            for step in steps:
                step_name = step.get('step_name', '')
                enabled = step.get('enabled', False)
                params = step.get('params', {})
                
                match step_name:
                    case 'join':
                        if enabled:
                            left_source_name = params.get('left_source_name', '')
                            right_source_name = params.get('right_source_name', '')
                            join_type = params.get('join_type', 'inner')
                            output_source_name = params.get('output_source_name', f"{left_source_name}_{right_source_name}_joined")
                            left_key = params.get('left_key', 'slide_id')
                            right_key = params.get('right_key', 'slide_id')
                            missing_policy = params.get('missing_policy', 'drop')
                            
                            if left_source_name not in self.sources:
                                logger.error("Left source for join not found: %s", left_source_name)
                                continue
                            if right_source_name not in self.sources:
                                logger.error("Right source for join not found: %s", right_source_name)
                                continue
                            left_source = self.sources[left_source_name]
                            right_source = self.sources[right_source_name]
                            output_source = Source(
                                source_name=output_source_name,
                                type=None  # Output source will be populated after join
                            )
                            
                            self.pipeline.add_step(JoinStep(
                                left_source=left_source,
                                right_source=right_source,
                                output_source=output_source,
                                left_key=left_key,
                                right_key=right_key,
                                join_type=join_type,
                                missing_policy=missing_policy
                            ))
                            
                            # Add intermediate source for step output
                            self.sources[output_source_name] = output_source
                            
                            logger.info("Added join step: %s", step_name)
                        else:
                            logger.info("Skipping disabled step: %s", step_name)
                    case 'ExampleDPSStep':
                        if enabled:
                            input_source_name = params.get('input_source_name', '')
                            output_source_name = params.get('output_source_name', 'example_output')
                            
                            if input_source_name not in self.sources:
                                logger.error("Input source for example step not found: %s", input_source_name)
                                continue
                            
                            output_source = Source(
                                source_name=output_source_name,
                                type=None  # Output source will be populated after step execution
                            )
                            
                            input_source = self.sources.get(input_source_name, None)
                            example_step = ExampleDPSStep(input_source=input_source, output_source=output_source)
                            self.pipeline.add_step(example_step)
                            
                            # Add intermediate source for step output
                            self.sources[output_source_name] = output_source
                            
                            logger.info("Added example DPS step: %s", step_name)
                        else:
                            logger.info("Skipping disabled step: %s", step_name)
                    case _:
                        logger.warning("Unknown DPS step: %s", step_name)


    def run(self) -> bool:
        """
        Run the data preparation pipeline.
        Returns:
            bool: True if the pipeline executed successfully, False otherwise.
        """
        logger.info("Running DPS on manifest: %s", self.manifest_path)
        
        status = self.pipeline.execute()
        logger.info("Data preparation complete.")
        return status


if __name__ == "__main__":
    if "RIScale" not in os.getcwd():
        os.chdir("RIScale")
    
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