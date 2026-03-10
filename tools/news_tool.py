from core.tool import Tool
from .news_scraper import get_news

class NewsTool(Tool):

    @property
    def name(self) -> str:
        return "news_converse"

    @property
    def description(self) -> str:
        return "Summarizes today's top news from the configured news website."

    def run(self, input_text: str | None = None) -> str:
        # input_text could allow filtering topics, but ignore for now
        articles = get_news()
        summaries = [a["title"] for a in articles]
        return "\n".join(summaries)
