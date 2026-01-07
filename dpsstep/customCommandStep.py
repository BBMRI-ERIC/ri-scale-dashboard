import json
import subprocess
from dpsdataset import Source
from dpsstep.DPSStep import DPSStep
import shlex
import logging
import os

logger = logging.getLogger(__name__)

class CustomCommandStep(DPSStep):
    def __init__(self, input_source:Source, command:str, fields:list[str]|None=None, execution_mode:str="per_row"):
        """
        Initialize the CustomCommandStep.
        Args:
            input_source (Source): The source of input data.
            command (str): The command to execute in the terminal. Can include placeholders for fields.
            fields (list[str]|None): List of field names to be used as placeholders in the command. If None, no placeholders will be used.
            execution_mode (str): Mode of execution, e.g., "per_row".
        """
        
        super().__init__(command)
        self.input_source = input_source
        self.command = command
        self.fields = fields if fields is not None else []
        self.execution_mode = execution_mode
        
    def __run_command__(self, command:str) -> subprocess.CompletedProcess:
        """
        Run a command in the terminal and return the completed process.
        Args:
            command (str): The command to execute.
        Returns:
            subprocess.CompletedProcess: The result of the command execution.
        """
        try:
            args = shlex.split(command)
            proc = subprocess.run(args, check=True, text=True, capture_output=True)
            return proc
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with error: {e}")
            return None
        except FileNotFoundError as e:
            logger.error(f"Command not found: {e}")
            return None
        
    def execute(self) -> bool:
        """
        Execute the custom command in Terminal
        """
        
        if self.execution_mode != "per_row":
            logger.info("Executing command '"+self.command+"' once without per-row processing.")
            self.__run_command__(self.command)
            return True
        
        logger.info("Executing command per row.")
            
        for _, row in self.input_source.get_data().iterrows():
            
            command_values = {field: None for field in self.fields}
            
            try:
                for field in command_values.keys():
                    command_values[field] = row[field]
            except Exception:
                logger.error("Cannot find field '" + field + "' in row with columns " + str(row.index.tolist()))
                
            final_command = self.command.format(**command_values)
                
            logger.info(f"Executing command: {final_command}")

            proc = self.__run_command__(final_command)
            if proc is None:
                logger.error("Command execution failed for command with values: " + str(command_values))
                #return False # Continue executing other rows even if one fails
            
        return True