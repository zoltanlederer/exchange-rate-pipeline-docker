# Exchange Rate Pipeline with Docker

Dockerised automated ETL pipeline that fetches daily exchange rate data from the Frankfurter API,
transforms it with pandas, and loads it into a PostgreSQL database.
Runs on a daily schedule using APScheduler.

Built on [exchange-rate-pipeline](https://github.com/zoltanlederer/exchange-rate-pipeline) — this repo adds Docker and Docker Compose to run the full stack locally in containers.

## What it does

- Portable and reproducible — runs identically on any machine with Docker
- Extracts daily EUR/USD, EUR/HUF, EUR/GBP and EUR/AUD exchange rates from the Frankfurter API
- Seeds the database with 2 years of historical data on first run
- Transforms raw API responses into clean, typed data using pandas
- Loads the results into a PostgreSQL database
- Runs automatically on a daily schedule using APScheduler

## Tech stack

- **Docker** — containerises the application
- **Docker Compose** — runs the app and PostgreSQL together as two connected containers
- **requests** — fetching data from the Frankfurter API
- **pandas** — transforming and cleaning the data
- **psycopg2-binary** — PostgreSQL driver, lets Python talk to PostgreSQL
- **APScheduler** — running the pipeline on a schedule
- **python-dotenv** — loading credentials from a `.env` file safely

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Installation

Clone the repo:
```bash
git clone https://github.com/zoltanlederer/exchange-rate-pipeline-docker
cd exchange-rate-pipeline-docker
```

Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

## Usage

Start the pipeline and database together:
```bash
docker compose up
```

Both containers will start — PostgreSQL first, then the app. The scheduler runs the pipeline daily at 17:00 CET. On the first run the database is seeded with 2 years of historical data.

To stop:
```bash
Ctrl+C
```

**Note:**       
The container runs in UTC. If you want to test the pipeline immediately, temporarily change the schedule in `scheduler.py` to a time in UTC, not your local time.

## Example output

After the first run, the database is seeded with 2 years of historical data:

| date       | base_currency | target_currency | rate   |
|------------|---------------|-----------------|--------|
| 2024-06-03 | EUR           | USD             | 1.0842 |
| 2024-06-03 | EUR           | HUF             | 391.40 |
| 2024-06-03 | EUR           | GBP             | 0.8517 |
| 2024-06-03 | EUR           | AUD             | 1.6290 |