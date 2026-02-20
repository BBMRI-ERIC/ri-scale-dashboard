from step.step import DPSStep
from dpsdataset.source import Source
import logging
logger = logging.getLogger(__name__)

class JoinStep(DPSStep):
    """
    A DPS step that joins two data sources based on a common key.
    """
    def __init__(self, left_source: Source, right_source: Source,output_source: Source, left_key: str, right_key: str, join_type: str = "inner", missing_policy: str = "drop", simulated: bool = True):
        """Initialize the JoinStep.
        Args:
            left_source (Source): The left data source to join.
            right_source (Source): The right data source to join.
            output_source (Source): The output data source to store the joined result.
            
            left_key (str): The key column in the left source to join on.
            right_key (str): The key column in the right source to join on.
            join_type (str): The type of join to perform (e.g., 'inner', 'left', 'right', 'outer').
            missing_policy (str): Policy for handling missing data ('drop', 'fill', etc.). # Not implemented yet.
        """
        
        super().__init__("Join Step", simulated=simulated)
        self.left_source = left_source
        self.right_source = right_source
        self.output_source = output_source
        self.left_key = left_key
        self.right_key = right_key
        self.join_type = join_type
        self.missing_policy = missing_policy


    def execute(self) -> bool:
        """Execute the join operation between the two sources."""
        logger.info("Joining between %s and %s", self.left_source.source_name, self.right_source.source_name)
        try:
            left_df = self.left_source.get_data()
            right_df = self.right_source.get_data()
            joined_df = left_df.merge(right_df, how=self.join_type, left_on=self.left_key, right_on=self.right_key)

            if self.missing_policy == "drop":
                before = len(joined_df)
                joined_df = joined_df.dropna()
                dropped = before - len(joined_df)
                if dropped:
                    logger.info("Dropped %d unmatched row(s) due to missing_policy=drop", dropped)

            self.output_source._data = joined_df
            logger.info("Output source %s has %d records.", self.output_source.source_name, len(joined_df))
            return True
        except Exception as e:
            logger.error("Error during step %s: %s", self.name, e)
            return False