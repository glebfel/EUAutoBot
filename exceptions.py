class BasicBotException(Exception):
    """Base class for all bot errors"""

    def __str__(self):
        return "Something goes wrong with bot"


class InvalidUrlError(BasicBotException):
    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f"Invalid link {self.url} was passed!"
