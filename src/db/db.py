import psycopg
from psycopg import sql

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def init_db(db_name: str):
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


def init_experiments_db():
    """
    Initializes the database and creates the tables for tracking experiments,
    artifacts, and data lineage using lookup tables for types and statuses.
    """
    db_name = 'experiments'
    print("Connecting to PostgreSQL to ensure database exists...")
    POSTGRES_MAINTENANCE_CONN_STRING = f"dbname='postgres' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"

    try:
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
        print(f"Details: {e}")
        return
    except Exception as e:
        print(f"\nAn unexpected error occurred during database creation check: {e}")
        return

    print("Connecting to the 'experiments' database to create experiment tracking tables...")
    POSTGRES_CONN_STRING = f"dbname='experiments' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"

    try:
        with psycopg.connect(POSTGRES_CONN_STRING) as con:
            with con.cursor() as cur:
                # 1. Create lookup tables for types and statuses
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS experiment_types (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS experiment_statuses (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS artifact_types (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL
                    );
                """)

                # 2. Populate lookup tables idempotently
                exp_types = ['CLUSTERING', 'DATASET_CREATION', 'FINE_TUNING', 'EMBEDDING_GENERATION', 'RAW_DATA_IMPORT']
                statuses = ['PENDING', 'RUNNING', 'COMPLETED', 'FAILED']
                art_types = ['MODEL', 'DATASET', 'VISUALIZATION', 'LOGS', 'VECTOR_COLLECTION', 'RAW_DATA']

                cur.executemany("INSERT INTO experiment_types (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", [(t,) for t in exp_types])
                cur.executemany("INSERT INTO experiment_statuses (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", [(s,) for s in statuses])
                cur.executemany("INSERT INTO artifact_types (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", [(a,) for a in art_types])

                # 3. Create main tables with foreign keys to lookup tables
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS experiments (
                        id UUID PRIMARY KEY,
                        name TEXT,
                        type_id INTEGER NOT NULL,
                        status_id INTEGER NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        notes TEXT,
                        CONSTRAINT fk_type FOREIGN KEY(type_id) REFERENCES experiment_types(id),
                        CONSTRAINT fk_status FOREIGN KEY(status_id) REFERENCES experiment_statuses(id)
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS experiment_params (
                        id UUID PRIMARY KEY,
                        experiment_id UUID NOT NULL,
                        params JSONB,
                        CONSTRAINT fk_experiment
                            FOREIGN KEY(experiment_id)
                            REFERENCES experiments(id)
                            ON DELETE CASCADE
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS experiment_artifacts (
                        id UUID PRIMARY KEY,
                        experiment_id UUID NOT NULL,
                        type_id INTEGER NOT NULL,
                        path TEXT NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        CONSTRAINT fk_experiment
                            FOREIGN KEY(experiment_id)
                            REFERENCES experiments(id)
                            ON DELETE CASCADE,
                        CONSTRAINT fk_type FOREIGN KEY(type_id) REFERENCES artifact_types(id)
                    );
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_artifact_path ON experiment_artifacts (path);")

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS experiment_dependencies (
                        experiment_id UUID NOT NULL,
                        artifact_id UUID NOT NULL,
                        CONSTRAINT fk_experiment
                            FOREIGN KEY(experiment_id)
                            REFERENCES experiments(id)
                            ON DELETE CASCADE,
                        CONSTRAINT fk_artifact
                            FOREIGN KEY(artifact_id)
                            REFERENCES experiment_artifacts(id)
                            ON DELETE CASCADE,
                        PRIMARY KEY (experiment_id, artifact_id)
                    );
                """)

            con.commit()
            print("Experiment tracking tables created or already exist.")

    except psycopg.OperationalError as e:
        print(f"\nError: Could not connect to the database 'experiments'.")
        print(f"Please check your connection settings and ensure the database server is running.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during experiment table creation: {e}")
