"""
Django management command to clean up orphaned media files.

Usage:
    python manage.py cleanup_media_files
    python manage.py cleanup_media_files --dry-run  # See what would be deleted without deleting
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from events.models import Media
import os


class Command(BaseCommand):
    help = 'Delete orphaned media files that are no longer referenced in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No files will be deleted'))
        
        # Get all file paths from database
        db_files = set()
        for media in Media.objects.all():
            if media.file:
                db_files.add(media.file.path)
        
        # Scan media directory
        media_root = settings.MEDIA_ROOT
        events_media_path = os.path.join(media_root, 'calculum', 'events')
        
        if not os.path.exists(events_media_path):
            self.stdout.write(self.style.WARNING(f'Media directory not found: {events_media_path}'))
            return
        
        orphaned_files = []
        total_size = 0
        
        # Walk through all files in media directory
        for root, dirs, files in os.walk(events_media_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                
                if filepath not in db_files:
                    orphaned_files.append(filepath)
                    total_size += os.path.getsize(filepath)
        
        if not orphaned_files:
            self.stdout.write(self.style.SUCCESS('No orphaned files found!'))
            return
        
        # Report findings
        self.stdout.write(self.style.WARNING(f'\nFound {len(orphaned_files)} orphaned file(s)'))
        self.stdout.write(f'Total size: {total_size / (1024*1024):.2f} MB\n')
        
        for filepath in orphaned_files:
            self.stdout.write(f'  - {filepath}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN: No files were deleted'))
            self.stdout.write('Run without --dry-run to actually delete these files')
        else:
            # Delete orphaned files
            deleted_count = 0
            for filepath in orphaned_files:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error deleting {filepath}: {e}'))
            
            self.stdout.write(self.style.SUCCESS(f'\nDeleted {deleted_count} orphaned file(s)'))
            
            # Clean up empty directories
            for root, dirs, files in os.walk(events_media_path, topdown=False):
                for dirname in dirs:
                    dirpath = os.path.join(root, dirname)
                    try:
                        if not os.listdir(dirpath):  # Directory is empty
                            os.rmdir(dirpath)
                            self.stdout.write(f'Removed empty directory: {dirpath}')
                    except Exception as e:
                        pass