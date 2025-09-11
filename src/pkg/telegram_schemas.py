from __future__ import annotations
from typing import List, Union, Literal, Optional
from enum import Enum
from pydantic import BaseModel
from datetime import datetime


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

class Answer(BaseModel):
    text: str
    voters: int
    chosen: bool

class Poll(BaseModel):
    question: str
    closed: bool
    total_voters: int
    answers: List[Answer]

class ReactionType(str, Enum):
    Emoji = 'emoji'
    Paid = 'paid'

class PaidReaction(BaseModel):
    type: Literal[ReactionType.Paid]
    count: int

class EmojiReaction(BaseModel):
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

class TextEntity(BaseModel):
    type: TextEntityType
    text: str
    href: Optional[str] = None
    document_id: Optional[str] = None
    collapsed: Optional[bool] = None

class MessageBase(BaseModel):
    id: int
    date: datetime # 2021-10-04T21:33:22
    date_unixtime: str
    text: Union[str, List[Union[TextEntity, str]]]
    text_entities: List[TextEntity]

class Service(MessageBase):
    type: Literal[MessageType.Service]
    actor: str
    actor_id: str
    action: MessageAction
    title: str
    message_id: Optional[int] = None

class Message(MessageBase):
    type: Literal[MessageType.Message]
    from_: str
    from_id: str
    edited: Optional[datetime] = None # 2021-10-04T21:33:22
    edited_unixtime: Optional[datetime] = None # 2021-10-04T21:33:22
    photo: Optional[str] = None
    photo_file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    reactions: Optional[List[Union[EmojiReaction, PaidReaction]]] = None
    poll: Optional[Poll] = None
    file: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[MimeType] = None
    thumbnail: Optional[str] = None
    thumbnail_file_size: Optional[int] = None
    duration_seconds: Optional[int] = None
    reply_to_message_id: Optional[int] = None
    forwarded_from: Optional[str] = None
    media_spoiler: Optional[bool] = None
    media_type: Optional[MediaType] = None
