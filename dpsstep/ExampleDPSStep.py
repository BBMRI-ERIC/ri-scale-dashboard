import logging
from DPSStep import DPSStep

logger = logging.getLogger(__name__)

class ExampleDPSStep(DPSStep):
    """
    An example implementation of a DPS step.
    """
    def __init__(self):
        super().__init__("Example Step")

    def execute(self, data: any) -> any:
        logger.info("Executing example step.")
        # Example processing logic
        return data