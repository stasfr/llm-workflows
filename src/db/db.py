import psycopg
from psycopg import sql

from src.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def init(db_name: str):
    """
    Initializes the database by creating it if it doesn't exist,
    then creating all necessary tables if they don't exist.
    """
    print("Connecting to PostgreSQL to ensure database exists...")
    POSTGRES_MAINTENANCE_CONN_STRING = f"dbname='postgres' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"

    try:
        # autocommit=True is required for CREATE DATABASE
        with psycopg.connect(POSTGRES_MAINTENANCE_CONN_STRING, autocommit=True) as con:
            with con.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                if not cur.fetchone():
                    print(f"Database '{db_name}' does not exist. Creating it...")
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                    print(f"Database '{db_name}' created successfully.")
                else:
                    print(f"Database '{db_name}' already exists.")

    except psycopg.OperationalError as e:
        print(f"\nError: Could not connect to the PostgreSQL server.")
        print(f"Please check your connection settings and ensure the PostgreSQL server is running.")
        print(f"Details: {e}")
        return
    except Exception as e:
        print(f"\nAn unexpected error occurred during database creation check: {e}")
        return

    print(f"Connecting to the '{db_name}' database to create tables...")
    POSTGRES_CONN_STRING = f"dbname='{db_name}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"

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
            print("Tables created or already exist.")

    except psycopg.OperationalError as e:
        print(f"\nError: Could not connect to the database '{db_name}'.")
        print(f"Please check your connection settings and ensure the database server is running.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during table creation: {e}")
