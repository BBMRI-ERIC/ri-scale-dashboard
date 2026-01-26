import logging
from dpsdataset import source
from step.step import DPSStep

logger = logging.getLogger(__name__)

class ExampleDPSStep(DPSStep):
    """
    An example implementation of a DPS step.
    """
    def __init__(self, input_source:source, output_source:source = None, simulated:bool=True):
        super().__init__("Example Step", simulated=simulated)
        self.input_source = input_source
        if output_source is None:
            self.output_source = input_source
        else:
            self.output_source = output_source

    def execute(self) -> bool:
        logger.info("Executing example step.")
        # Example processing logic
        self.input_source.data = "test string"
        self.output_source.data = self.input_source.data
        logger.info("Example step completed.")
        return True