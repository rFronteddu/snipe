from .news_tool import NewsTool
from .interest_tool import SubscribeInterestTool, CheckInterestTool
from .list_tools_tool import ListToolsTool
from core.memory import Memory

def load_tools():
    # persistent memory
    memory = Memory("data/memory.json")

    base_tools = [
        NewsTool(),
        SubscribeInterestTool(memory),
        CheckInterestTool(memory)
    ]

    tools = {t.name: t for t in base_tools}

    tools["list_tools"] = ListToolsTool(tools)

    return tools