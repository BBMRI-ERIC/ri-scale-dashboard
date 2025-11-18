import logging
from dpsdataset.Source import Source
from dpsstep.DPSStep import DPSStep
import dpsstep.ExampleDPSStep

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


    def execute(self) -> bool:
        """Deprecated: Execute all steps in the pipeline sequentially."""
        overall_status = True
        
        for step in self.steps:
            logger.info("Executing step: %s", step.name)
            status = step.execute()
            overall_status = overall_status and status
            
        return overall_status
    
    
    def run_next_step(self) -> bool:
        if not self.steps:
            logger.warning("No steps in the pipeline to run.")
            return False
        step = self.steps.pop(0)
        logger.info("Running next step: %s", step.name)
        return step.execute()
    
    
    def has_steps_left(self) -> bool:
        return len(self.steps) > 0
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = DPSPipeline()
    sources = {}
    
    source_in = Source(source_name="example_source", type=None)
    source_intermediate = Source(source_name="example_source_intermediate", type=None)
    source_out = Source(source_name="example_source_final", type=None)
    
    sources[source_in.source_name] = source_in
    sources[source_intermediate.source_name] = source_intermediate
    sources[source_out.source_name] = source_out
    
    pipeline.add_step(dpsstep.ExampleDPSStep.ExampleDPSStep(input_source=source_in, output_source=source_intermediate))
    pipeline.add_step(dpsstep.ExampleDPSStep.ExampleDPSStep(input_source=source_intermediate, output_source=source_out))
    
    logger.info("DPS Pipeline initialized with %d steps.", len(pipeline.steps))
    
    status = True
    while status:
        status = pipeline.run_next_step()
        
        logger.info("Pipeline has %d steps left.", len(pipeline.steps))
    logger.info("DPS Pipeline execution completed.")
        