from core.tool import Tool
from typing import Dict

class ListToolsTool(Tool):
    def __init__(self, tools):
        self.tools = tools

    @property
    def name(self) -> str:
        return "list_tools"

    @property
    def description(self) -> str:
        return "List all tools the agent can use, with optional descriptions."

    def run(self, input_text: str | None = None) -> str:
        # if user asks for details, return names + descriptions
        if input_text and "describe" in input_text.lower():
            return "\n".join([f"{t}: {tool.description}" for t, tool in self.tools.items() if t != "list_tools"])
        # default: just return names
        return "\n".join([t for t in self.tools.keys() if t != "list_tools"])