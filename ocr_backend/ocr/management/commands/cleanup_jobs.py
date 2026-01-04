# ocr/management/commands/cleanup_jobs.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ocr.models import OCRJob


class Command(BaseCommand):
    help = 'Clean up old OCR jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete jobs older than this many days (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_jobs = OCRJob.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['done', 'rejected']
        )
        
        count = old_jobs.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No old jobs to clean up')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'Would delete {count} jobs older than {days} days'
                )
            )
            for job in old_jobs[:10]:  # Show first 10
                self.stdout.write(
                    f'  - Job {job.id}: {job.status} (created: {job.created_at})'
                )
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            old_jobs.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {count} old jobs'
                )
            )