import json
import subprocess
from dpsdataset import Source
from dpsstep.DPSStep import DPSStep
import shlex
import logging
import os

logger = logging.getLogger(__name__)

class CustomCommandStep(DPSStep):
    def __init__(self, input_source:Source, output_source:Source, command:str, input_column:str = None, output_column:str = None):
        super().__init__(command)
        self.input_source = input_source
        self.output_source = output_source
        self.input_column = input_column
        self.output_column = output_column
        self.command = command
        
    def execute(self) -> bool:
        """
        Execute the custom command in Terminal
        """
        
        for _, row in self.input_source.get_data().iterrows():
            try:
                input_file = row[self.input_column]
                input_folder = os.path.dirname(str(input_file)) or '.'
                
                output_file = input_file + "_output"
                output_folder = os.path.dirname(str(output_file)) or '.'
                
                if '{input_file}' in self.command and '{output_folder}' in self.command:
                    final_command = self.command.format(input_file=input_file, output_folder=output_folder)
                    logger.debug(f"Command of type \"programm -i input_file -o output_folder\"")
                elif '{input_file}' in self.command and '{output_file}' in self.command:
                    final_command = self.command.format(input_file=input_file, output_file=output_file)
                    logger.debug(f"Command of type \"programm -i input_file -o output_file\"")
                elif '{input_folder}' in self.command and '{output_folder}' in self.command:
                    final_command = self.command.format(input_folder=input_folder, output_folder=output_folder)
                    logger.debug(f"Command of type \"programm -i input_folder -o output_folder\"")
                    break
                else:
                    final_command = self.command
                    logger.debug(f"Command without specific input/output placeholders")
                    break  # Only need to format once for the command execution
            except Exception:
                logger.error("Error formatting command with input and output columns")
                return False

        self.command = final_command
        try:
            proc = subprocess.run(self.command, shell=True, check=True, text=True, capture_output=True)
            meta = json.loads(proc.stdout.strip())
            for key, value in meta.items():
                logger.info(f"Command output - {key}: {value}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with error: {e}")
            return False
        return True