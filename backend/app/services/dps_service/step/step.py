
class DPSStep:
    """
    Base class for data preparation steps.
    Each step should implement the `execute` method.
    """
    def __init__(self, name:str, simulated:bool=False):
        self.name = name
        self.simulated = simulated

    def execute(self) -> bool:
        """
        Execute the data preparation step.
        Output:
            bool: True if the step executed successfully, False otherwise.
        """
        raise NotImplementedError("Each step must implement the execute method.")
    
    def undo(self) -> bool:
        """
        Undo the data preparation step if possible.
        Output:
            bool: True if the undo operation was successful, False otherwise.
        """
        return True  # By default, assume undo is successful (or not needed)
    

