import argparse
import secrets
import string
import bcrypt
import psycopg
import os
from dotenv import load_dotenv

# --- Database Configuration ---
# The script expects the following environment variables for DB connection:
# DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
# They should be in a .env file in the project root.

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
    """Main function to reset a user's password."""
    parser = argparse.ArgumentParser(description="Reset a user's password.")
    parser.add_argument("email", type=str, help="The email of the user whose password to reset.")
    args = parser.parse_args()

    email = args.email
    new_plain_password = generate_password()
    new_hashed_password = hash_password(new_plain_password)

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
            with conn.cursor() as cur:
                # Update the user's password
                cur.execute(
                    "UPDATE users SET password = %s WHERE email = %s",
                    (new_hashed_password, email)
                )

                # Check if any row was updated
                if cur.rowcount == 0:
                    print(f"Error: User with email '{email}' not found.")
                else:
                    conn.commit()
                    print(f"Password for user '{email}' has been reset successfully.")
                    print(f"New Password: {new_plain_password}")

    except psycopg.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
