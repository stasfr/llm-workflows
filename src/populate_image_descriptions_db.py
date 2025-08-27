import os
import duckdb
from PIL import Image
from tqdm import tqdm
import models
from process_tg_data import count_json_items, stream_filtered_tg_data
import json

PLAIN_DATA_DIR = 'F:\\tg-chat-exports\\jeldor'

WORKING_DIR = './output'
FILTERED_FILE = os.path.join(WORKING_DIR, 'filtered_telegram_data.json')

DB_FILE = os.path.join(WORKING_DIR, 'image_descriptions.duckdb')
DB_TABLE_NAME = 'image_descriptions'

def setup_database():
    """Creates a DuckDB connection and the table for image descriptions."""
    con = duckdb.connect(DB_FILE)
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
            post_id INTEGER PRIMARY KEY,
            date TIMESTAMP,
            text VARCHAR,
            photo_description VARCHAR,
            photo_tag VARCHAR,
            photo_structured_description VARCHAR,
            description_usage VARCHAR,
            tag_usage VARCHAR,
            structured_description_usage VARCHAR,
            description_time FLOAT,
            tag_time FLOAT,
            structured_description_time FLOAT
        );
    """)
    return con

def get_processed_ids(con):
    """Gets the set of post_ids that are already in the database."""
    return set(row[0] for row in con.execute(f"SELECT post_id FROM {DB_TABLE_NAME}").fetchall())

def process_images():
    """
    Iterates through telegram data, generates descriptions for photos,
    and stores them in a DuckDB database.
    """
    print("Initializing image description model...")

    image_describer = models.ImageDescription(model_name="google/gemma-3-4b")

    print("Setting up database...")
    con = setup_database()
    processed_ids = get_processed_ids(con)

    total_items = count_json_items(FILTERED_FILE, 'item')
    print(f"Found {total_items} items in the filtered data.")
    print(f"{len(processed_ids)} items already processed. Resuming...")

    data_stream = stream_filtered_tg_data(FILTERED_FILE)

    with tqdm(total=total_items, desc="Processing posts") as pbar:
        for item in data_stream:
            pbar.update(1)
            post_id = item.get('id')

            if not post_id or post_id in processed_ids:
                continue

            if 'photo' in item and item['photo']:
                image_path = os.path.join(PLAIN_DATA_DIR, item['photo'])

                if not os.path.exists(image_path):
                    # pbar.set_postfix_str(f"Photo not found: {item['photo']}", refresh=True)
                    continue

                try:
                    with Image.open(image_path) as img:
                        # Generate description
                        description, desc_usage, desc_time = image_describer.get_description(img)
                        tag, tag_usage, tag_time = image_describer.get_tag(img)
                        structured_description, struct_desc_usage, struct_desc_time = image_describer.get_structured_description(img)

                        # Insert into database
                        con.execute(
                            f"""INSERT INTO {DB_TABLE_NAME} (
                                post_id, date, text,
                                photo_description, photo_tag, photo_structured_description,
                                description_usage, tag_usage, structured_description_usage,
                                description_time, tag_time, structured_description_time
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                    print(f"Error processing image for post {post_id}: {e}")

    con.close()
    print("Processing complete.")

if __name__ == "__main__":
    process_images()
