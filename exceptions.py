class BasicBotException(Exception):
    """Base class for all bot errors"""

    def __str__(self):
        return "Something goes wrong with bot"


class NotUrlError(BasicBotException):
    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f"{self.url} is not url!"


class AnotherUrlError(BasicBotException):
    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f"{self.url} is url of the another web page!"


class CarAttributeEmptyError(BasicBotException):
    def __init__(self, attr: str = None):
        self.attr = attr

    def __str__(self):
        return self.attr
