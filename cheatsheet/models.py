from django.db import models


class AlgorithmCategory(models.Model):
    """Categories for organizing algorithms (e.g., Graphs, DP, Strings)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Algorithm Categories"
    
    def __str__(self):
        return self.name


class Algorithm(models.Model):
    """An algorithm with title, description, and code"""
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('c', 'C'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        AlgorithmCategory,
        on_delete=models.CASCADE,
        related_name='algorithms',
        null=True,
        blank=True
    )
    description = models.TextField(
        blank=True,
        help_text="Brief explanation of the algorithm"
    )
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='python',
        help_text="Programming language"
    )
    code = models.TextField(
        help_text="Code for the algorithm"
    )
    time_complexity = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., O(n log n)"
    )
    space_complexity = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., O(n)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category__name', 'title']
    
    def __str__(self):
        if self.category:
            return f"{self.category.name} - {self.title}"
        return self.title