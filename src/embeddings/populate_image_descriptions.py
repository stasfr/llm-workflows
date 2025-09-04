import os
import json
import psycopg
from psycopg import sql
from PIL import Image
import ijson

from typing import Optional, Callable, Generator

from llm.image_description import ImageDescription
from config import (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    STORAGE_FOLDER
)
from utils.count_json_items import count_json_items

def stream_filtered_tg_data(filename: str) -> Generator[dict, None, None]:
    """
    Generator to stream data from a JSON file which is a list of objects.
    Yields dictionaries.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yield from ijson.items(f, 'item')
    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        raise
    except json.JSONDecodeError:
        print(f"Error: Could not read JSON from file {filename}.")
        raise

def _get_processed_ids(con: psycopg.Connection, db_table_name: str) -> set[int]:
    """Gets the set of post_ids that are already in the database."""
    with con.cursor() as cur:
        cur.execute(sql.SQL("SELECT post_id FROM {}").format(sql.Identifier(db_table_name)))
        return set(row[0] for row in cur.fetchall())

def populate_image_descriptions(
    project_name: str,
    project_snapshot: str,
    db_table_name: str,
    model_name: str,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> None:
    """
    Iterates through telegram data, generates descriptions for photos,
    and stores them in a PostgreSQL database.
    """
    PHOTOS_DIR = os.path.join(STORAGE_FOLDER, 'photos', project_name)
    PROJECT_DIR = os.path.join(STORAGE_FOLDER, 'projects', f"{project_name}_{project_snapshot}")
    FILTERED_FILE = os.path.join(PROJECT_DIR, 'filtered_telegram_data.json')

    POSTGRES_CONN_STRING = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"

    image_describer = ImageDescription(model_name=model_name)

    con = None
    try:
        con = psycopg.connect(POSTGRES_CONN_STRING)

        processed_ids = _get_processed_ids(con, db_table_name)

        if not os.path.exists(FILTERED_FILE):
            print(f"Warning: Filtered data file not found at {FILTERED_FILE}")
            return

        total_items = count_json_items(FILTERED_FILE, 'item')
        if total_items == 0:
            return

        data_stream = stream_filtered_tg_data(FILTERED_FILE)
        processed_count = 0

        with con.cursor() as cur:
            for item in data_stream:
                processed_count += 1
                if progress_callback:
                    progress_callback(processed_count, total_items)

                post_id = item.get('id')
                if not post_id or post_id in processed_ids:
                    continue

                if 'photo' in item and item['photo']:
                    image_path = os.path.join(PHOTOS_DIR, item['photo'])

                    if not os.path.exists(image_path):
                        continue

                    try:
                        with Image.open(image_path) as img:
                            description, desc_usage, desc_time = image_describer.get_description(img)
                            tag, tag_usage, tag_time = image_describer.get_tag(img)
                            structured_description, struct_desc_usage, struct_desc_time = image_describer.get_structured_description(img)

                            cur.execute(
                                sql.SQL('''INSERT INTO {} (
                                    post_id, date, text,
                                    photo_description, photo_tag, photo_structured_description,
                                    description_usage, tag_usage, structured_description_usage,
                                    description_time, tag_time, structured_description_time
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (post_id) DO NOTHING''').format(sql.Identifier(db_table_name)),
                                (
                                    post_id,
                                    item.get('date'),
                                    item.get('text'),
                                    description,
                                    tag,
                                    structured_description,
                                    json.dumps(desc_usage) if desc_usage else None,
                                    json.dumps(tag_usage) if tag_usage else None,
                                    json.dumps(struct_desc_usage) if struct_desc_usage else None,
                                    desc_time,
                                    tag_time,
                                    struct_desc_time
                                )
                            )
                            processed_ids.add(post_id)
                    except Exception as e:
                        print(f"Warning: Error processing image for post {post_id}: {e}")
            con.commit()

    except psycopg.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
    finally:
        if con:
            con.close()
