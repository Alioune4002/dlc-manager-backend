from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from .tasks import process_expired_products

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(
        process_expired_products,
        trigger="cron",
        hour=0,
        minute=0,
        id="process_expired_products",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()