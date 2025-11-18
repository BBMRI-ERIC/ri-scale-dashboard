
class DPSStep:
    """
    Base class for data preparation steps.
    Each step should implement the `execute` method.
    """
    def __init__(self, name:str):
        self.name = name

    def execute(self) -> bool:
        """
        Execute the data preparation step.
        Output:
            bool: True if the step executed successfully, False otherwise.
        """
        raise NotImplementedError("Each step must implement the execute method.")
    

