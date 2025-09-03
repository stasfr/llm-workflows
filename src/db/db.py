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
                print("Creating 'image_descriptions' table...")
                cur.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS image_descriptions (
                        post_id INTEGER PRIMARY KEY,
                        date TIMESTAMP,
                        text TEXT,
                        photo_description TEXT,
                        photo_tag TEXT,
                        photo_structured_description TEXT,
                        description_usage JSONB,
                        tag_usage JSONB,
                        structured_description_usage JSONB,
                        description_time FLOAT,
                        tag_time FLOAT,
                        structured_description_time FLOAT
                    );
                """))
                print("'image_descriptions' table created or already exists.")

                print("Creating 'users' table...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                print("'users' table created or already exists.")

            con.commit()
            print("\nDatabase initialization completed successfully!")

    except psycopg.OperationalError as e:
        print(f"\nError: Could not connect to the database.")
        print(f"Please check your connection settings and ensure the database server is running.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    init()
