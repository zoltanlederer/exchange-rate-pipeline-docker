"""ETL pipeline for fetching and storing daily exchange rate data."""

import requests
import pandas as pd
import psycopg2
import logging
from datetime import date
from db import get_connection, setup_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ETLPipeline:
    def __init__(self):
        """Initialise the pipeline with base currency and target currencies."""
        self.currencies = ['HUF', 'GBP', 'USD', 'AUD']
        self.base_currency = 'EUR'

    def extract(self):
        """Get today's exchange rates."""
        logging.info("Extracting data...")
        try:
            url = f'https://api.frankfurter.app/latest?from={self.base_currency}&to={",".join(self.currencies)}'
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f'Connection failed: {e}')
            raise
    
    def transform(self, data):
        """The method receives a dictionary and returns a clean pandas DataFrame where each row is one currency pair."""
        logging.info("Transforming data...")
        rows = []
        for currency, rate in data['rates'].items():
            rows.append({
                'date': data['date'],
                'base_currency': data['base'],
                'target_currency': currency,
                'rate': rate
            })
        df = pd.DataFrame(rows)
        return df
    
    def load(self, df):
        """Receives the DataFrame and writes each row into the PostgreSQL exchange_rates table."""
        logging.info("Loading data...")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            for index, row in df.iterrows(): # .iterrows() always returns two things on each iteration: the row index (0, 1, 2, 3) and the row data
                values = (row['date'], row['base_currency'], row['target_currency'], row['rate'])
                cursor.execute("INSERT INTO exchange_rates (date, base_currency, target_currency, rate) VALUES (%s, %s, %s, %s) ON CONFLICT (date, target_currency) DO NOTHING", values)

            conn.commit()
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            logging.error(f'Database error: {e}')
            raise

    def run(self):
        """Run the full ETL pipeline — extract, transform, and load."""
        setup_database()
        try:
            if self.is_database_empty():
                self.run_historical()
            else:
                data = self.extract()
                df = self.transform(data)
                self.load(df)
        except Exception as e:
            logging.error(f'Pipeline failed: {e}')
            return None
        
    def seed_historical_data(self):
        """Seed the database with 2 years of historical data on the first run."""
        logging.info("Extracting past 2 years data...")
        today = date.today()
        two_years_ago = today.replace(year=today.year - 2)
        try:
            url = f'https://api.frankfurter.app/{two_years_ago}..{today}?from={self.base_currency}&to={",".join(self.currencies)}'
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f'Connection failed: {e}')
            raise
    
    def transform_historical(self, data):
        """Transform historical API response into a DataFrame — one row per date and currency pair."""
        logging.info("Transforming data...")
        rows = []
        for date, currencies in data['rates'].items():
            for cur, rate in currencies.items():
                rows.append({
                    'date': date,
                    'base_currency': data['base'],
                    'target_currency': cur,
                    'rate': rate
                })

        df = pd.DataFrame(rows)
        return df
            
    def run_historical(self):
        """Run the full ETL pipeline for historical data — seed_historical_data, transform_historical, and load."""
        try:
            data = self.seed_historical_data()
            df = self.transform_historical(data)
            self.load(df)
        except Exception as e:
            logging.error(f'Pipeline failed: {e}')
            return None
        
    def is_database_empty(self):
        """Check database if it is empty or not."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            count = cursor.execute('SELECT COUNT (id) FROM exchange_rates')
            count = cursor.fetchone()
            cursor.close()
            conn.close()
            return count[0] == 0
        except psycopg2.Error as e:
            logging.error(f'Database error: {e}')
            raise


if __name__ == '__main__':
    pipeline = ETLPipeline()
    pipeline.run()
