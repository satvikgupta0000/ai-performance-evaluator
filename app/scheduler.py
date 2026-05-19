import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from app.core.db import fetch_all
from app.core.evaluator import run_team_evaluation

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")

def scheduled_annual_evaluation():
    year = datetime.now(IST).year
    logger.info(f"[Scheduler] March 15 annual evaluation triggered for year {year}")

    managers = fetch_all("""
        SELECT u.id FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE r.name = 'manager' AND u.is_active = TRUE
    """)

    for mgr in managers:
        results = run_team_evaluation(mgr["id"], year)
        for r in results:
            logger.info(f"[Scheduler] {r['employee']}: {r['status']}")

def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=IST)
    scheduler.add_job(
        scheduled_annual_evaluation,
        trigger=CronTrigger(month=3, day=15, hour=0, minute=0, timezone=IST),
        id="annual_evaluation",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[Scheduler] Started — annual evaluation scheduled for March 15 00:00 IST")
    return scheduler
