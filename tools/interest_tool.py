from core.tool import Tool
from core.memory import Memory
from .news_scraper import get_news  # our mocked scraper
from typing import List

class SubscribeInterestTool(Tool):

    def __init__(self, memory: Memory):
        self.memory = memory

    @property
    def name(self):
        return "subscribe_interest"

    @property
    def description(self):
        return "Subscribe to a topic for notifications when news matches it."

    def run(self, input_text: str = "") -> str:
        self.memory.append("interests", input_text)
        return f"Subscribed to news about '{input_text}'"


class CheckInterestTool(Tool):

    def __init__(self, memory: Memory):
        self.memory = memory

    @property
    def name(self):
        return "check_interest"

    @property
    def description(self):
        return "Check if any recent news matches your subscribed interests."

    def run(self, input_text="") -> str:
        interests = self.memory.get("interests", [])
        articles = get_news()
        hits: List[str] = []

        for article in articles:
            title = article["title"].lower()
            for topic in interests:
                if topic.lower() in title:
                    hits.append(article["title"])

        if hits:
            return "News matching your interests:\n" + "\n".join(hits)
        return "No news matches your interests."
