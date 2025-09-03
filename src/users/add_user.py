import argparse
import secrets
import string
import bcrypt
import psycopg
import os
import uuid
from dotenv import load_dotenv

# --- Database Configuration ---
# The script expects the following environment variables for DB connection:
# DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
#
# You can place them in a .env file in the project root.
# Example .env file:
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=your_db_name
#
# --- Database Table Schema ---
# The script will automatically create the 'users' table if it doesn't exist
# with the following structure:
#
# CREATE TABLE users (
#     id UUID PRIMARY KEY,
#     email TEXT UNIQUE NOT NULL,
#     password TEXT NOT NULL,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
# );
#

def create_table_if_not_exists(conn):
    """Checks if the 'users' table exists and creates it if it does not."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'users'
            );
        """)
        exists = cur.fetchone()[0]
        if not exists:
            cur.execute("""
                CREATE TABLE users (
                    id UUID PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Table 'users' created.")

def generate_password(length=16):
    """Generates a random password with letters, digits, and symbols."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def hash_password(password):
    """Hashes the password using bcrypt and returns it as a string."""
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def main():
    """Main function to add a user to the database."""
    parser = argparse.ArgumentParser(description="Add a new user to the database.")
    parser.add_argument("email", type=str, help="The email of the user to add.")
    args = parser.parse_args()

    email = args.email
    plain_password = generate_password()
    hashed_password = hash_password(plain_password)
    user_id = uuid.uuid4()

    # Load environment variables from .env file
    load_dotenv()

    try:
        # Connect to the PostgreSQL database
        with psycopg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME")
        ) as conn:
            # Ensure the table exists
            create_table_if_not_exists(conn)

            with conn.cursor() as cur:
                # Insert the new user
                cur.execute(
                    "INSERT INTO users (id, email, password) VALUES (%s, %s, %s)",
                    (user_id, email, hashed_password)
                )
                conn.commit()

        print(f"User '{email}' created successfully.")
        print(f"Generated Password: {plain_password}")

    except psycopg.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
