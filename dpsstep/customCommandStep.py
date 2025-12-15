import json
import subprocess
from dpsdataset import Source
from dpsstep.DPSStep import DPSStep
import shlex
import logging
import os

logger = logging.getLogger(__name__)

class CustomCommandStep(DPSStep):
    def __init__(self, input_source:Source, output_source:Source, input_column, output_column, command: str):
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
    
                output_folder = os.path.dirname(str(input_file)) or '.'
                
                final_command = self.command.format(input=input_file, output=output_folder)
            except Exception:
                logger.error("Error formatting command with input and output columns")
                return False
                pass

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