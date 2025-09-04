import os
import sys
import psycopg
from psycopg import sql

# This is needed to be able to run the script directly and still import the config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

def init():
    """
    Initializes the database by creating all necessary tables if they don't exist.
    """
    print("Connecting to the database...")
    POSTGRES_CONN_STRING = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"

    try:
        with psycopg.connect(POSTGRES_CONN_STRING) as con:
            with con.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS posts (
                        id UUID PRIMARY KEY,
                        post_id INTEGER UNIQUE NOT NULL,
                        date VARCHAR(100),
                        edited VARCHAR(100),
                        from_id VARCHAR(100) NOT NULL,
                        text TEXT,
                        reactions JSONB
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS media (
                        id UUID PRIMARY KEY,
                        name TEXT NOT NULL,
                        post_id INTEGER NOT NULL,
                        mime_type TEXT NOT NULL,
                        CONSTRAINT fk_post
                            FOREIGN KEY(post_id)
                            REFERENCES posts(post_id)
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS media_data (
                        id UUID PRIMARY KEY,
                        media_id UUID NOT NULL,
                        description TEXT,
                        tag TEXT,
                        structured_description TEXT,
                        description_usage JSONB,
                        tag_usage JSONB,
                        structured_description_usage JSONB,
                        description_time FLOAT,
                        tag_time FLOAT,
                        structured_description_time FLOAT,
                        CONSTRAINT fk_media
                            FOREIGN KEY(media_id)
                            REFERENCES media(id)
                    );
                """)

            con.commit()

    except psycopg.OperationalError as e:
        print(f"\nError: Could not connect to the database.")
        print(f"Please check your connection settings and ensure the database server is running.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    init()
