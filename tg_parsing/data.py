from .telegram import TextEntity
from typing import TypedDict, List, NotRequired

class MappedTelegramData(TypedDict):
    id: int
    date: str
    text_entities: List[TextEntity]
    photo: NotRequired[str]

class ParsedTelegramData(TypedDict):
    id: int
    date: str
    text: NotRequired[str]
    photo: NotRequired[str]
