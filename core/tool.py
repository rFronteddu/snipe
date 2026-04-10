from abc import ABC, abstractmethod
from typing import Dict, Any

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

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """
        JSON schema describing tool input parameters.
        """
        pass

    def schema(self) -> Dict[str, Any]:
        """
        Export tool definition for the planner.
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }

    @abstractmethod
    def run(self, params: Dict[str, Any]) -> str:
        """
        Execute the tool using structured parameters.
        """
        pass
