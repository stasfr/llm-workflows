import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Model


class TgExportsModel(Model):
    __tablename__ = "tg_exports"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[str] = mapped_column(unique=True)
    data_path: Mapped[str]
    photos_path: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('UTC', now())"))

    posts: Mapped[list["PostsModel"]] = relationship(back_populates="channel")


class PostsModel(Model):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    post_id: Mapped[int] = mapped_column(unique=True)
    date: Mapped[Optional[str]]
    edited: Mapped[Optional[str]]
    from_id: Mapped[str] = mapped_column(ForeignKey("tg_exports.channel_id"))
    post_text: Mapped[Optional[str]]
    reactions: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('UTC', now())"))

    channel: Mapped["TgExportsModel"] = relationship(back_populates="posts")
    media: Mapped[list["MediaModel"]] = relationship(back_populates="post")


class MediaModel(Model):
    __tablename__ = "media"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id"))
    mime_type: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('UTC', now())"))

    post: Mapped["PostsModel"] = relationship(back_populates="media")
    data: Mapped["MediaDataModel"] = relationship(back_populates="media_data", uselist=False)


class MediaDataModel(Model):
    __tablename__ = "media_data"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    media_id: Mapped[UUID] = mapped_column(ForeignKey("media.id"), unique=True)
    description: Mapped[Optional[str]]
    tag: Mapped[Optional[str]]
    structured_description: Mapped[Optional[str]]
    description_usage: Mapped[Optional[dict]] = mapped_column(JSONB)
    tag_usage: Mapped[Optional[dict]] = mapped_column(JSONB)
    structured_description_usage: Mapped[Optional[dict]] = mapped_column(JSONB)
    description_time: Mapped[Optional[float]]
    tag_time: Mapped[Optional[float]]
    structured_description_time: Mapped[Optional[float]]
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('UTC', now())"))

    media_data: Mapped["MediaModel"] = relationship(back_populates="data")
