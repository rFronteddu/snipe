class Tool:
    """All tools follow the same interface."""
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def run(self, input):
        return self.func(input)
