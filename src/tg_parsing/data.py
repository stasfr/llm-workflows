from typing import TypedDict, NotRequired

class ParsedTelegramData(TypedDict):
    id: int
    date: str
    text: NotRequired[str]
    photo: NotRequired[str]
