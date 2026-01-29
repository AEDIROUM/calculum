from django.core.management.base import BaseCommand
from board.models import Problem

class Command(BaseCommand):
    help = 'Fetch and update difficulties for all problems from Kattis/LeetCode.'

    def handle(self, *args, **options):
        updated = 0
        for problem in Problem.objects.all():
            if 'kattis.com' in problem.link:
                if problem._fetch_kattis_difficulty():
                    updated += 1
            elif 'leetcode.com' in problem.link:
                if problem._fetch_leetcode_difficulty():
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated difficulties for {updated} problems.'))
