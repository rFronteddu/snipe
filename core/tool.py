from abc import ABC, abstractmethod

class Tool(ABC):
    """
    Abstract base class for all tools.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the tool (used for LLM to call it)
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Short description of what the tool does
        """
        pass

    @abstractmethod
    def run(self, input_text: str = "") -> str:
        """
        Execute the tool with the given input and return a string result
        """
        pass
