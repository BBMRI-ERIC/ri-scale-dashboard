import logging
from dpsstep.DPSStep import DPSStep

logger = logging.getLogger(__name__)

class DPSPipeline:
    """
    Class representing a DPS pipeline.
    Holds a sequence of data preparation steps to be executed.
    """
    
    def __init__(self, steps: list[DPSStep] | None = None):
        if steps:
            self.steps: list.List[DPSStep] = steps
        else:
            self.steps: list.List[DPSStep] = []


    def add_step(self, step: DPSStep):
        self.steps.append(step)
        
    def add_steps(self, steps: list[DPSStep]):
        self.steps.extend(steps)

    def execute(self, data):
        for step in self.steps:
            logger.info("Executing step: %s", step.name)
            data = step.execute(data)
            
            patches, label = data[0]
            logger.info("Step %s produced data with %d patches.", step.name, len(patches))
            
        return data
    
    