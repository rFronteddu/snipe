def get_news():
    """
    Mocked news scraper: returns a list of articles.
    Each article is a dictionary with at least a 'title' field.
    """
    return [
        {"title": "OpenAI releases GPT-5 prototype"},
        {"title": "NASA announces new moon mission"},
        {"title": "Stock markets hit record highs today"},
        {"title": "New breakthrough in renewable energy"},
        {"title": "Robotics conference showcases next-gen AI"},
    ]
