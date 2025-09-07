from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from src.database import Model


class Posts(Model):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    post_id: Mapped[int]
    date: Mapped[Optional[str]]
    edited: Mapped[Optional[str]]
    from_id: Mapped[str]
    text: Mapped[Optional[str]]
    reactions: Mapped[Optional[dict]] = mapped_column(JSONB)

class Media(Model):
    __tablename__ = "media"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    post_id: Mapped[int]
    mime_type: Mapped[str]

class MediaData(Model):
    __tablename__ = "media_data"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    media_id: Mapped[UUID]
    description: Mapped[Optional[str]]
    tag: Mapped[Optional[str]]
    structured_description: Mapped[Optional[str]]
    description_usage: Mapped[Optional[dict]] = mapped_column(JSONB)
    tag_usage: Mapped[Optional[dict]] = mapped_column(JSONB)
    structured_description_usage: Mapped[Optional[dict]] = mapped_column(JSONB)
    description_time: Mapped[Optional[float]]
    tag_time: Mapped[Optional[float]]
    structured_description_time: Mapped[Optional[float]]