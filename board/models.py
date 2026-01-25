from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Session(models.Model):
    season = models.CharField(
        choices=[
            ('autumn', 'Automne'),
            ('winter', 'Hiver'),
            ('summer', 'Été')
        ]
    )
    
    year = models.IntegerField()
    
    local = models.CharField(
        default='AA-3189'
    )
    
    time = models.TimeField()
    
    day = models.CharField(
        choices=[
            ('monday', 'Lundi'),
            ('tuesday', 'Mardi'),
            ('wednesday', 'Mercredi'),
            ('thursday', 'Jeudi'),
            ('friday', 'Vendredi'),
            ('saturday', 'Samedi'),
            ('sunday', 'Dimanche')
        ],
        default='wednesday'
    )
    
    class Meta:
        unique_together = ('season', 'year')
        ordering = ['-year', 'season']
    
    def __str__(self):
        return f"{self.get_season_display()} {self.year}"


class Meet(models.Model):
    date = models.DateField(
        null=True,
        blank=True,
    )
    
    session = models.ForeignKey(
        Session,
        related_name="meets",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    description = models.TextField(
        null=False,
        blank=True,
        default=''
    )
    
    theme = models.CharField(
        default="",
        blank=True
    )
    
    contest_link = models.CharField(
        default="",
        blank=True,
        null=False
    )
    
    get_problems = models.BooleanField(
        default=False
    )
    
    managers = models.ManyToManyField(
        User,
        blank=True,
        related_name="meets_managed"
    )
    
    def save(self, *args, **kwargs):
        # Auto-determine and get/create session
        if not self.session:
            month = self.date.month
            year = self.date.year
            # Define seasons based on UdeM academic calendar
            # Automne: September-December
            # Hiver: January-April
            # Été: May-August
            if 9 <= month <= 12:
                season = 'autumn'
            elif 1 <= month <= 4:
                season = 'winter'
            else:  # 5-8
                season = 'summer'
            # Get or create the session
            self.session, created = Session.objects.get_or_create(
                season=season,
                year=year,
                defaults={
                    'local': 'AA-3189',
                    'time': datetime.strptime('18:00', '%H:%M').time()
                }
            )
        super().save(*args, **kwargs)
        
        # Auto-fetch problems from Kattis contest if get_problems is True
        # Run in background to avoid blocking the save
        if self.get_problems and self.contest_link and 'kattis.com/contests/' in self.contest_link:
            try:
                self._fetch_kattis_problems()
            except Exception as e:
                # Log but don't fail the save
                print(f"Warning: Failed to fetch Kattis problems for meet {self.id}: {str(e)}")
    
    def _fetch_kattis_problems(self):
        """Fetch problems from Kattis contest and create Problem objects"""
        import requests
        from bs4 import BeautifulSoup
        import re
        
        try:
            if not self.contest_link:
                return
            
            # Extract contest ID from URL
            contest_match = re.search(r'/contests/([^/?]+)', self.contest_link)
            if not contest_match:
                return
            
            try:
                response = requests.get(self.contest_link, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Network error fetching contest: {str(e)}")
                return
            
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                print(f"Error parsing HTML: {str(e)}")
                return
            
            # Find all problem links in the contest page
            # Look for links that might be /problems/xxx or /contests/xxx/problems/xxx
            problem_links = soup.find_all('a', href=re.compile(r'/(?:contests/[^/]+/)?problems/[^/?]+'))
            
            for link in problem_links:
                try:
                    problem_url = link.get('href')
                    if not problem_url:
                        continue
                    
                    # Remove contest context from URL - convert /contests/xxx/problems/yyy to /problems/yyy
                    problem_url = re.sub(r'/contests/[^/]+/problems/', '/problems/', problem_url)
                    
                    # Make sure it's a full URL
                    if not problem_url.startswith('http'):
                        base_url = 'https://open.kattis.com' if 'open.kattis.com' in self.contest_link else 'https://kattis.com'
                        problem_url = base_url + problem_url
                    
                    # Get or create the problem
                    Problem.objects.get_or_create(
                        link=problem_url,
                        defaults={
                            'platform': 'Kattis',
                            'done': self
                        }
                    )
                except Exception as e:
                    # Continue on individual problem creation errors
                    print(f"Error creating problem: {str(e)}")
                    continue
                    
        except Exception as e:
            # Silent fail - don't break the save if fetching fails
            print(f"Failed to fetch Kattis problems: {e}")
    
    def get_algo_content(self):
        """Read and return the algo file content, or None if only comments/blanks or file doesn't exist"""
        import os
        algo_path = os.path.join(
            os.path.dirname(__file__),
            'meets',
            str(self.date.year),
            f"{self.date.month:02d}",
            f"{self.date.day:02d}.py"
        )
        try:
            with open(algo_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has actual code (not just comments and blanks)
            for line in content.split('\n'):
                stripped = line.strip()
                # Skip empty lines and comments
                if stripped and not stripped.startswith('#'):
                    return content
            
            # File only contains comments and blanks
            return None
        except FileNotFoundError:
            return None
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        import os
        algo_path = os.path.join(
            'board/meets',
            str(self.date.year),
            f"{self.date.month:02d}",
            f"{self.date.day:02d}.py"
        )
        result = f"Rencontre {self.date.strftime('%d/%m/%Y')}"
        if self.theme:
            result += f" - {self.theme}"
        result += f" [{algo_path}]"
        return result


class Problem(models.Model):
    link = models.CharField(
        primary_key=True
    )
    
    platform = models.CharField()
    
    done = models.ForeignKey(
        Meet,
        related_name="problems",
        on_delete=models.PROTECT
    )
    
    solution_link = models.CharField(
        blank=True,
        default=""
    )
    
    def __str__(self):
        # Try to extract title from URL
        import re
        match = re.search(r'/problems?/([^/?]+)', self.link)
        if match:
            title = match.group(1).replace('-', ' ').replace('_', ' ').title()
            return f"{self.platform} - {title}"
        return f"{self.platform} - {self.link[:50]}"