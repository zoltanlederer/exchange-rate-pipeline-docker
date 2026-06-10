"""Schedule to run ETLPipeline every day at 17:00 CET."""

from pipeline import ETLPipeline
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

pipeline = ETLPipeline()
scheduler = BlockingScheduler()
scheduler.add_job(pipeline.run, 'cron', hour=17, minute=0)
logging.info("Scheduler started. Running every day at 17:00 CET.")
scheduler.start()