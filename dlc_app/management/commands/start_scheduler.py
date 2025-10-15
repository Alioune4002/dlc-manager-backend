from django.core.management.base import BaseCommand
from dlc_app.scheduler import start

class Command(BaseCommand):
    help = 'Start the APScheduler for periodic tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting scheduler...'))
        start()
        self.stdout.write(self.style.SUCCESS('Scheduler started.'))