from .time_tool import TimeTool
from .weather_tool import WeatherTool
from core.memory import Memory
# Import other tools here as you add them:
# from tools.github_tool import GitHubTool

def load_tools(memory_path="data/memory.json"):
    """
    Initializes and returns a dictionary of available tools.
    """

    # 1. Initialize persistent memory (shared across tools that need it)
    memory = Memory(memory_path)

    # 2. Instantiate your tools
    # We create a list first for easy iteration or conditional loading
    base_tools = [
        WeatherTool(),
        TimeTool(),
        # Future tools go here:
        # GitHubReaderTool(),
    ]

    # 3. Create the lookup dictionary { "tool_name": tool_instance }
    # This uses the .name property from your Tool(ABC)
    tools_map = {t.name: t for t in base_tools}

    return tools_map