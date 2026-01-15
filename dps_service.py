"""
Data Preparation for Exploitation Service (DPS) module.
USAGE EXAMPLE:
    python DPSService.py -m ./example_manifest.yaml -v
"""

import argparse
import os
import logging
import yaml
from dps_pipeline import DPSPipeline
from dpsstep.custom_command import CustomCommandStep
import dpsdataset.loaders as loaders
from dpsstep.example_dps_step import ExampleDPSStep
from dpsstep.join import JoinStep
from dpsdataset.source import FileDiscoveryStrategy, CSVFileStrategy, Source
import re

logger = logging.getLogger("dpsService")

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
        
    # helper to add a join step
    def __handle_join__(self, params) -> bool:
        left_source_name = params.get('left_source_name', '')
        right_source_name = params.get('right_source_name', '')
        join_type = params.get('join_type', 'inner')
        output_source_name = params.get('output_source_name', f"{left_source_name}_{right_source_name}_joined")
        left_key = params.get('left_key', 'slide_id')
        right_key = params.get('right_key', 'slide_id')
        missing_policy = params.get('missing_policy', 'drop')

        if left_source_name not in self.sources:
            logger.error("Left source for join not found: %s", left_source_name)
            return False
        if right_source_name not in self.sources:
            logger.error("Right source for join not found: %s", right_source_name)
            return False
        
        left_source = self.sources[left_source_name]
        right_source = self.sources[right_source_name]
        output_source = Source(
            source_name=output_source_name,
            data_source_strategy=None  # Output source will be populated after join
        )

        self.pipeline.add_step(JoinStep(
            left_source=left_source,
            right_source=right_source,
            output_source=output_source,
            left_key=left_key,
            right_key=right_key,
            join_type=join_type,
            missing_policy=missing_policy,
            simulated=self.pipeline.simulated
        ))

        self.sources[output_source_name] = output_source
        return True

    # helper to add the example DPS step
    def __handle_example__(self, params) -> bool:
        input_source_name = params.get('input_source_name', '')
        output_source_name = params.get('output_source_name', 'example_output')

        if input_source_name not in self.sources:
            logger.error("Input source for example step not found: %s", input_source_name)
            return False

        input_source = self.sources[input_source_name]
        output_source = Source(
            source_name=output_source_name,
            data_source_strategy=None  # Output source will be populated after step execution
        )

        example_step = ExampleDPSStep(input_source=input_source, output_source=output_source, simulated=self.pipeline.simulated)
        self.pipeline.add_step(example_step)

        # register intermediate output source
        self.sources[output_source_name] = output_source
        return True
    
    def __handle_custom__(self, params) -> bool:
        if params is None or params == {}:
            return False
        
        command = params.get('command', None)
        
        if command is None:
            return False
        
        input_source_name = params.get('input_source_name', None)
        #output_source_name = params.get('output_source_name', 'custom_command_output')
        
        input_source = self.sources.get(input_source_name, None)
        
        execution_mode = params.get('execution_mode', 'per_row')
        
        if execution_mode == "per_row" and input_source_name is None:
            logger.error("Input source is needed with per-row execution mode.")
            return False
        elif execution_mode == "per_row" and input_source is None:
            logger.error("Given input source not found: %s", input_source_name)
            return False
        
        fields = re.findall(r'\{(\w+)\}', command)
        
        self.pipeline.add_step(CustomCommandStep(
            input_source=input_source, 
            command=command, fields=fields,
            execution_mode=execution_mode,
            simulated=self.pipeline.simulated
            ))
        
        return True
    
    def __handle_load__(self, params) -> bool:
        error = False
        source_name = params.get('output_source_name', None)
        mode = params.get('mode', None)
        path = params.get('path', None)
        include = params.get('include', None)
        recursive = params.get('recursive', False)
        column_info = params.get('columns', None)
        file_type = params.get('file_type', None)
        directory_mode = params.get('directory_mode', False)
        
        if source_name is None:
            logger.error("Output source name not set")
            error = True
        if mode is None:
            logger.error("mode (file/discovery) not set")
            error = True
        if path is None:
            logger.error("path not set")
            error = True
        if column_info is None and mode == "discovery":
            logger.error("No further information about column structure provided")
            error = True
        else:
            if mode == "discovery":
                path_column_name = column_info.get('column_name', 'path')
                regex_filename_to_columnnames = column_info.get('filename_to_columnname', None)
                if regex_filename_to_columnnames is None:
                    logger.error("No regex given to extract key name from file name")
                    error = True
            elif mode == "csv_file" and column_info is not None:
                header = column_info.get('header', False)
                delimiter = column_info.get('delimiter', ',')

        if error:
            return False

        loader = loaders.getLoader(file_type)
        
        if mode == "discovery":
            source = Source(
                source_name=source_name,
                data_source_strategy=FileDiscoveryStrategy(
                    path=path,
                    include=include,
                    recursive=recursive,
                    id_pattern=regex_filename_to_columnnames,
                    loader=loader,
                    column_name=path_column_name,
                    directory_mode=directory_mode
                )
            )
            self.sources[source.source_name] = source
        elif mode == "csv_file":
            source = Source(
                source_name=source_name,
                data_source_strategy=CSVFileStrategy(
                    path=path,
                    delimiter=delimiter,
                    header=header
                )
            )
            self.sources[source.source_name] = source 

        return True
        
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
            
            simulated = manifest.get('simulated', True)
            if simulated:
                logger.info("Running in SIMULATED mode.")
                self.pipeline.simulated = True
            else:
                logger.info("Running in PRODUCTION mode.")
                self.pipeline.simulated = False
            
            # defined_sources = manifest.get('sources', [])
            self.sources: dict[str, Source] = {}

        
        
        # -----------------------------------------------------------------------------------------
        # Parse and add DPS steps and their intermediate data source results to the pipeline
        # -----------------------------------------------------------------------------------------
            steps = manifest.get('dps_steps', manifest.get('job_steps', []))
            for step in steps:
                step_name = step.get('step_name', '')
                step_type = step.get('type', '')
                enabled = step.get('enabled', True)
                params = step.get('params', {})
                
                if not enabled:
                    logger.info("Skipping disabled step: \"%s\"", step_name)
                    continue

                match step_type:
                    case 'load':
                        if not self.__handle_load__(params):
                            continue
                        logger.info("Added Source loader: \"%s\"", step_name)
                    case 'join':
                        if not self.__handle_join__(params):
                            continue
                        logger.info("Added join step: \"%s\"", step_name)
                    case 'ExampleDPSStep':
                        if not self.__handle_example__(params):
                            continue
                        logger.info("Added example DPS step: \"%s\"", step_name)
                    case 'custom_command':
                        if not self.__handle_custom__(params):
                            continue
                        #logger.warning("[POTENTIALLY INSECURE] Added custom step: \"%s\" (%s)", step_name, params.get('command', 'no command'))
                        logger.info("Added custom command step: \"%s\" (%s)", step_name, params.get('command', 'no command'))
                    case _:
                        logger.error("Invalid step: \"%s\"", step_name)


    def run(self) -> bool:
        """
        Run the data preparation pipeline.
        Returns:
            bool: True if the pipeline executed successfully, False otherwise.
        """
        
        logger.info("Running DPS on manifest: %s", self.manifest_path)
        
        status = True
        while status:
            status = self.pipeline.run_next_step()
            
            logger.debug("Pipeline has %d steps left.", len(self.pipeline.steps))
        logger.info("DPS Pipeline execution completed.")
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