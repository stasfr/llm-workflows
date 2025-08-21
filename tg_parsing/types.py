from typing import TypedDict, List, Union, Literal, NotRequired
from enum import Enum

# From src/types/telegram.ts

MimeType = Literal[
    'application/pdf',
    'video/mp4',
    'image/jpeg',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'video/quicktime',
    'audio/mpeg',
    'audio/ogg'
]

class MessageType(str, Enum):
    Service = 'service'
    Message = 'message'

MessageAction = Literal['create_channel', 'pin_message']

MediaType = Literal[
    'video_file',
    'animation',
    'audio_file',
    'video_message',
    'voice_message'
]

class Answer(TypedDict):
    text: str
    voters: int
    chosen: bool

class Poll(TypedDict):
    question: str
    closed: bool
    total_voters: int
    answers: List[Answer]

class ReactionType(str, Enum):
    Emoji = 'emoji'
    Paid = 'paid'

class PaidReaction(TypedDict):
    type: Literal[ReactionType.Paid]
    count: int

class EmojiReaction(TypedDict):
    type: Literal[ReactionType.Emoji]
    count: int
    emoji: str

TextEntityType = Literal[
    'plain',
    'link',
    'mention',
    'text_link',
    'italic',
    'bold',
    'underline',
    'email',
    'strikethrough',
    'spoiler',
    'bot_command',
    'code',
    'custom_emoji',
    'blockquote',
    'phone',
    'hashtag'
]

class TextEntity(TypedDict):
    type: TextEntityType
    text: str
    href: NotRequired[str]
    document_id: NotRequired[str]
    collapsed: NotRequired[bool]

class MessageBase(TypedDict):
    id: int
    date: str # 2021-10-04T21:33:22
    date_unixtime: str
    text: Union[str, List[Union[TextEntity, str]]]
    text_entities: List[TextEntity]

class Service(MessageBase):
    type: Literal[MessageType.Service]
    actor: str
    actor_id: str
    action: MessageAction
    title: str
    message_id: NotRequired[int]

class Message(MessageBase):
    type: Literal[MessageType.Message]
    from_: str  # 'from' is a reserved keyword in Python, using 'from_' instead.
    from_id: str
    edited: NotRequired[str]
    edited_unixtime: NotRequired[str]
    photo: NotRequired[str]
    photo_file_size: NotRequired[int]
    width: NotRequired[int]
    height: NotRequired[int]
    reactions: NotRequired[List[Union[EmojiReaction, PaidReaction]]]
    poll: NotRequired[Poll]
    file: NotRequired[str]
    file_name: NotRequired[str]
    file_size: NotRequired[int]
    mime_type: NotRequired[MimeType]
    thumbnail: NotRequired[str]
    thumbnail_file_size: NotRequired[int]
    duration_seconds: NotRequired[int]
    reply_to_message_id: NotRequired[int]
    forwarded_from: NotRequired[str]
    media_spoiler: NotRequired[bool]
    media_type: NotRequired[MediaType]

class TgData(TypedDict):
    name: str
    type: str
    id: int
    messages: List[Message]
