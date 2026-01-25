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
        blank=False,
        default=''
    )
    
    theme = models.CharField(
        default="",
        blank=True
    )
    
    managers = models.ManyToManyField(
        User,
        blank=True,
        related_name="meets_managed"
    )
    
    def save(self, *args, **kwargs):
        import os
        from django.core.exceptions import ValidationError
        algo_path = os.path.join(
            os.path.dirname(__file__),
            'meets',
            str(self.date.year),
            f"{self.date.month:02d}",
            f"{self.date.day:02d}.py"
        )
        if not os.path.exists(algo_path):
            raise ValidationError(f"Algo file does not exist: {algo_path}")
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
    
    def get_algo_content(self):
        """Read and return the algo file content, or None if only comments/blanks"""
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
            return "# Algo non disponible"
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        if self.theme:
            return f"Rencontre {self.date.strftime('%d/%m/%Y')} - {self.theme}"
        return f"Rencontre {self.date.strftime('%d/%m/%Y')}"


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