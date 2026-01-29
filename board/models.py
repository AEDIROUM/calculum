from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Session(models.Model):
    season = models.CharField(
        max_length=10,
        choices=[
            ('autumn', 'Automne'),
            ('winter', 'Hiver'),
            ('summer', 'Été')
        ]
    )
    
    year = models.IntegerField()
    
    local = models.CharField(
        max_length=100,
        default='AA-3189'
    )
    
    time = models.TimeField()
    
    day = models.CharField(
        max_length=10,
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
    
    # REMOVED: theme field - use problem categories instead
    
    contest_link = models.CharField(
        max_length=500,
        default="",
        blank=True,
        null=False
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
        
        # Auto-fetch problems from Kattis contest if contest_link exists
        if self.contest_link and 'kattis.com/contests/' in self.contest_link:
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
                    
                    # Get or create the problem and add this meet to it
                    problem, created = Problem.objects.get_or_create(
                        link=problem_url,
                        defaults={
                            'platform': 'Kattis'
                        }
                    )
                    # Add this meet to the problem's meets
                    problem.meets.add(self)
                except Exception as e:
                    # Continue on individual problem creation errors
                    print(f"Error creating problem: {str(e)}")
                    continue
                    
        except Exception as e:
            # Silent fail - don't break the save if fetching fails
            print(f"Failed to fetch Kattis problems: {e}")
    
    def get_categories(self):
        """Get all unique categories from problems in this meet"""
        categories = set()
        for problem in self.problems.all():
            categories.update(problem.categories.all())
        return sorted(categories, key=lambda c: c.name)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Rencontre {self.date.strftime('%d/%m/%Y')}"


class Problem(models.Model):
    link = models.CharField(
        max_length=500,
        primary_key=True
    )
    
    platform = models.CharField(
        max_length=100
    )
    
    meets = models.ManyToManyField(
        Meet,
        related_name="problems",
        blank=True
    )
    
    # Categories/themes for this problem (from cheatsheet app)
    categories = models.ManyToManyField(
        'cheatsheet.AlgorithmCategory',
        related_name='problems',
        blank=True,
        help_text="Algorithm categories/themes for this problem"
    )
    
    solution_link = models.CharField(
        max_length=500,
        blank=True,
        default=""
    )
    
    difficulty = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )
    
    difficulty_number = models.FloatField(
        null=True,
        blank=True,
        default=None
    )
    
    def _fetch_kattis_difficulty(self):
        """Fetch difficulty from Kattis problem page"""
        import requests
        from bs4 import BeautifulSoup
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            response = requests.get(self.link, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the difficulty card
            diff_card = soup.find('div', class_='metadata-difficulty-card')
            if diff_card:
                # Extract difficulty number and level
                spans = diff_card.find_all('span')
                if len(spans) >= 2:
                    # First span has difficulty number
                    diff_num_text = spans[0].get_text(strip=True)
                    # Second span with "text-lg" has difficulty level
                    diff_level_text = None
                    for span in spans:
                        if 'text-lg' in span.get('class', []):
                            diff_level_text = span.get_text(strip=True)
                            break
                    
                    if diff_num_text and diff_level_text:
                        try:
                            self.difficulty_number = float(diff_num_text)
                            self.difficulty = f"{diff_num_text} {diff_level_text}"
                            self.save(update_fields=['difficulty', 'difficulty_number'])
                            return True
                        except (ValueError, TypeError):
                            pass
            return False
        except Exception as e:
            print(f"Error fetching Kattis difficulty for {self.link}: {str(e)}")
            return False
    
    def _fetch_leetcode_difficulty(self):
        """Fetch difficulty from LeetCode problem page"""
        import requests
        from bs4 import BeautifulSoup
        import re
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            response = requests.get(self.link, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for difficulty in the page content
            # LeetCode stores it in JSON in script tags
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    # Try to find difficulty in the data structure
                    if isinstance(data, dict):
                        if 'difficulty' in data:
                            difficulty = data['difficulty']
                            self.difficulty = difficulty
                            self.save(update_fields=['difficulty'])
                            return True
                except:
                    pass
            
            # Fallback: try to find in HTML text
            # Look for patterns like "Easy", "Medium", "Hard"
            text = soup.get_text()
            for level in ['Hard', 'Medium', 'Easy']:
                if level in text:
                    # Find if it's near problem info
                    if re.search(rf'Difficulty[:\s]+{level}', text):
                        self.difficulty = level
                        self.save(update_fields=['difficulty'])
                        return True
            
            return False
        except Exception as e:
            print(f"Error fetching LeetCode difficulty for {self.link}: {str(e)}")
            return False
    
    def get_difficulty(self):
        """Get difficulty, fetching if necessary"""
        if self.difficulty:
            return self.difficulty
        
        # Try to fetch if not cached
        if 'kattis.com' in self.link:
            self._fetch_kattis_difficulty()
        elif 'leetcode.com' in self.link:
            self._fetch_leetcode_difficulty()
        
        return self.difficulty or "—"
    
    def get_difficulty_level(self):
        """Extract difficulty level for styling (Easy, Medium, Hard, etc.)"""
        if not self.difficulty:
            return None
        
        difficulty_lower = self.difficulty.lower()
        if 'easy' in difficulty_lower:
            return 'easy'
        elif 'medium' in difficulty_lower:
            return 'medium'
        elif 'hard' in difficulty_lower:
            return 'hard'
        
        # For Kattis numeric difficulties
        if self.difficulty_number:
            if self.difficulty_number < 3.0:
                return 'easy'
            elif self.difficulty_number < 5.0:
                return 'medium'
            else:
                return 'hard'
        
        return None
    
    def __str__(self):
        # Try to extract title from URL
        import re
        match = re.search(r'/problems?/([^/?]+)', self.link)
        if match:
            title = match.group(1).replace('-', ' ').replace('_', ' ').title()
            return f"{self.platform} - {title}"
        return f"{self.platform} - {self.link[:50]}"