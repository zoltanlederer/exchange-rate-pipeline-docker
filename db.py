"""Database connection and table setup for the exchange rate pipeline."""

import psycopg2
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Reads .env file and loads the variables into the environment so os.getenv() can find them
load_dotenv()

def get_connection():
    """Create and return a connection to the PostgreSQL database."""
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    dbname = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    return psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)


def setup_database():
    """Create the exchange_rates table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            base_currency CHAR(3) NOT NULL,
            target_currency CHAR(3) NOT NULL,
            rate FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (date, target_currency)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Database ready.")


if __name__ == "__main__":
    setup_database()