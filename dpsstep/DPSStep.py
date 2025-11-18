from dpsdataset.Source import Source


class DPSStep:
    """
    Base class for data preparation steps.
    Each step should implement the `execute` method.
    """
    def __init__(self, name:str):
        self.name = name

    def execute(self, data: Source) -> Source:
        """
        Execute the data preparation step.
        Input:
            data: The input data to be processed.
        Output:
            The processed data.
        """
        raise NotImplementedError("Each step must implement the execute method.")
    

