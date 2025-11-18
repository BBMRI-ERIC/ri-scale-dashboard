import DPSStep
from dpsdataset.Source import Source
import logging
logger = logging.getLogger(__name__)

class JoinStep(DPSStep):
    """
    A DPS step that joins two data sources based on a common key.
    """
    def __init__(self, left_source: Source, right_source: Source, left_key: str, right_key: str, join_type: str = "inner", output_source_name: str = "joined_source", missing_policy: str = "drop"):
        super().__init__("Join Step")
        self.left_source = left_source
        self.right_source = right_source
        self.left_key = left_key
        self.right_key = right_key
        self.join_type = join_type
        self.output_source_name = output_source_name
        self.missing_policy = missing_policy

    def execute(self, data: Source) -> Source:
        logger.info("Executing join step between %s and %s", self.left_source.source_name, self.right_source.source_name)
        left_df = self.left_source.data
        right_df = self.right_source.data
        
        