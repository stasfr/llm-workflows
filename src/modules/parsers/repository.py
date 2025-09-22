import json
import os
import aiosqlite
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.config import STORAGE_FOLDER
from src.modules.parsers.schemas import PostModel
from src.modules.parsers.dto import CreatePost


class ParsersRepository:
    @classmethod
    async def get_experiment_db_path(cls, experiment_id: UUID) -> str:
        """Get the SQLite database path for an experiment."""
        experiment_dir = os.path.join(STORAGE_FOLDER, str(experiment_id))
        os.makedirs(experiment_dir, exist_ok=True)
        return os.path.join(experiment_dir, "dataset.db")

    @classmethod
    async def create_tables(cls, experiment_id: UUID) -> None:
        """Create necessary tables in the experiment's SQLite database."""
        db_path = await cls.get_experiment_db_path(experiment_id)

        async with aiosqlite.connect(db_path) as db:
            # Create posts table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    post_id INTEGER NOT NULL,
                    date TEXT,
                    edited TEXT,
                    post_text TEXT,
                    reactions TEXT,
                    has_media BOOLEAN DEFAULT FALSE,
                    from_id TEXT,
                    created_at TEXT DEFAULT (datetime('now', 'utc'))
                )
            """)

            # Create medias table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS medias (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    mime_type TEXT,
                    post_id TEXT,
                    created_at TEXT DEFAULT (datetime('now', 'utc')),
                    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE SET NULL
                )
            """)

            # Create media_datas table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS media_datas (
                    id TEXT PRIMARY KEY,
                    description TEXT,
                    tag TEXT,
                    structured_description TEXT,
                    description_usage TEXT,
                    tag_usage TEXT,
                    structured_description_usage TEXT,
                    description_time REAL,
                    tag_time REAL,
                    structured_description_time REAL,
                    media_id TEXT,
                    created_at TEXT DEFAULT (datetime('now', 'utc')),
                    FOREIGN KEY (media_id) REFERENCES medias(id) ON DELETE SET NULL
                )
            """)

            await db.commit()

    @classmethod
    async def add_one_post_with_media(cls, experiment_id: UUID, tg_export_id: UUID, payload: CreatePost) -> Optional[PostModel]:
        """Add a post with its media to the experiment's SQLite database."""
        # Generate UUIDs for the new records
        post_uuid = str(uuid4())
        media_uuids = [str(uuid4())
                       for _ in payload.media] if payload.media else []

        # Prepare reactions JSON
        reactions_json = (
            json.dumps([r.model_dump() for r in payload.reactions])
            if payload.reactions is not None
            else None
        )

        # Prepare media data
        media_data = []
        if payload.media:
            for i, media in enumerate(payload.media):
                media_data.append({
                    'id': media_uuids[i],
                    'name': media.name,
                    'mime_type': media.mime_type,
                    'post_id': post_uuid
                })

        db_path = await cls.get_experiment_db_path(experiment_id)

        async with aiosqlite.connect(db_path) as db:
            # Insert post
            await db.execute("""
                INSERT INTO posts (id, post_id, date, edited, post_text, reactions, has_media, from_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_uuid,
                payload.post_id,
                payload.date.isoformat() if payload.date else None,
                payload.edited.isoformat() if payload.edited else None,
                payload.post_text,
                reactions_json,
                payload.has_media,
                str(tg_export_id)
            ))

            # Insert media records
            for media in media_data:
                await db.execute("""
                    INSERT INTO medias (id, name, mime_type, post_id)
                    VALUES (?, ?, ?, ?)
                """, (
                    media['id'],
                    media['name'],
                    media['mime_type'],
                    media['post_id']
                ))

                # Insert empty media_data record
                media_data_uuid = str(uuid4())
                await db.execute("""
                    INSERT INTO media_datas (id, media_id)
                    VALUES (?, ?)
                """, (media_data_uuid, media['id']))

            await db.commit()

            # Fetch and return the created post
            cursor = await db.execute("""
                SELECT * FROM posts WHERE id = ?
            """, (post_uuid,))

            row = await cursor.fetchone()
            if row:
                # Convert SQLite row to PostModel
                return PostModel(
                    id=UUID(row[0]),
                    post_id=row[1],
                    date=datetime.fromisoformat(row[2]) if row[2] else None,
                    edited=datetime.fromisoformat(row[3]) if row[3] else None,
                    post_text=row[4],
                    reactions=json.loads(row[5]) if row[5] else None,
                    from_id=UUID(row[7]) if row[7] else None,
                    created_at=datetime.fromisoformat(row[8])
                )

        return None
