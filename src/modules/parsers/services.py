from typing import Generator
from pydantic import ValidationError

from src.config import STORAGE_FOLDER

import os
import json
import ijson

from src.pkg.telegram_schemas import Message

from src.modules.parsers.dto import StartParsing, CreatePost, CreateMedia
from src.modules.parsers.repository import ParsersRepository

from src.modules.tg_exports.repository import TgExportsRepository
from src.modules.experiments.repository import ExperimentsRepository


def stream_raw_tg_data(filename: str) -> Generator[dict, None, None]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yield from ijson.items(f, 'messages.item')
    except FileNotFoundError:
        raise ValueError(f"File not found at {filename}")
    except json.JSONDecodeError:
        raise ValueError(f"Could not decode JSON from file {filename}")


async def parse_raw_telegram_data(payload: StartParsing) -> None:
    tg_export = await TgExportsRepository.get_one_by_id(payload.tg_export_id)

    if not tg_export:
        raise ValueError(
            f"Telegram export with ID {payload.tg_export_id} not found")

    # Verify experiment exists
    experiment = await ExperimentsRepository.get_one_by_id(payload.experiment_id)
    if not experiment:
        raise ValueError(
            f"Experiment with ID {payload.experiment_id} not found")

    # Create SQLite tables for the experiment if they don't exist
    await ParsersRepository.create_tables(payload.experiment_id)

    PROJECT_DIR = os.path.join(
        STORAGE_FOLDER, tg_export.data_path.lstrip('\\/'))

    RAW_DATA_FILE = os.path.join(PROJECT_DIR, 'raw_data.json')
    GARBAGE_FILE = os.path.join(PROJECT_DIR, 'garbage.json')

    garbage_ids = []
    garbage_list = []

    if os.path.exists(GARBAGE_FILE) and payload.apply_filters:
        with open(GARBAGE_FILE, 'r', encoding='utf-8') as f:
            try:
                garbage_data = json.load(f)
                garbage_ids = garbage_data.get('garbage_ids', [])
                garbage_list = garbage_data.get('garbage_list', [])
            except json.JSONDecodeError:
                raise ValueError(
                    f"Could not decode garbage file at {GARBAGE_FILE}")

    try:
        with open(RAW_DATA_FILE, 'r', encoding='utf-8') as f:
            total_messages = sum(1 for _ in ijson.items(f, 'messages.item'))

        if total_messages == 0:
            raise ValueError("No messages found in the file.")

        raw_tg_data = stream_raw_tg_data(RAW_DATA_FILE)
        result: list[CreatePost] = []
        garbage_ids_set = set(garbage_ids)

        for item in raw_tg_data:
            if item.get('type') == 'message':
                if item.get('id') in garbage_ids_set:
                    continue
                try:
                    message = Message.model_validate(item)

                    if message.text_entities or message.photo:
                        text = ""
                        if message.text_entities:
                            text = "".join(
                                entity.text for entity in message.text_entities)
                            for garbage in garbage_list:
                                text = text.replace(garbage, '')
                            text = text.strip()

                        media_list = []
                        if message.photo:
                            mime_type = message.mime_type
                            if not mime_type:
                                file_ext = os.path.splitext(
                                    message.photo)[1].lower()
                                mime_types = {
                                    '.jpg': 'image/jpeg',
                                    '.jpeg': 'image/jpeg',
                                    '.png': 'image/png',
                                    '.gif': 'image/gif',
                                    '.webp': 'image/webp',
                                    '.bmp': 'image/bmp',
                                }
                                mime_type = mime_types.get(file_ext)

                            media = CreateMedia(
                                name=message.photo,
                                mime_type=mime_type
                            )
                            media_list.append(media)

                        create_post_payload = CreatePost(
                            post_id=message.id,
                            date=message.date,
                            edited=message.edited,
                            post_text=text,
                            reactions=message.reactions,
                            media=media_list,
                            has_media=len(media_list) > 0
                        )

                        if create_post_payload.post_text or create_post_payload.has_media:
                            result.append(create_post_payload)
                            await ParsersRepository.add_one_post_with_media(
                                payload.experiment_id,
                                payload.tg_export_id,
                                create_post_payload
                            )

                except ValidationError as e:
                    print(e)
                    pass

    except Exception as e:
        raise ValueError(f"Stream processing error: {e}")
