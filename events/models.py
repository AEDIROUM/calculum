from django.db import models
from django.utils.text import slugify


class Event(models.Model):
    title = models.CharField(
        max_length=200
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text='Auto-generated URL slug from title'
    )
    
    start = models.DateField(
        null=True,
        blank=True
    )
    
    end = models.DateField(
        null=True,
        blank=True
    )
    
    summary = models.TextField()
    
    # Server proxy fields
    server_port = models.IntegerField(
        blank=True,
        null=True,
        help_text='Port number for proxied server (e.g., 8080). Leave empty if no server.'
    )
    
    is_active = models.BooleanField(
        default=False,
        help_text='Enable/disable access to the proxied server'
    )
    
    hidden = models.BooleanField(
        default=True,
        help_text='Hide this event from the public events page'
    )
    
    class Meta:
        ordering = ['-title']
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not set
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure uniqueness
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def has_active_server(self):
        """Check if event has an active proxied server"""
        return self.server_port is not None and self.is_active
    
    
class Media(models.Model):
    event = models.ForeignKey(
        Event,
        related_name="medias",
        on_delete=models.CASCADE
    )
    
    file = models.FileField(
        upload_to='calculum/events/%Y/%m/'
    )
    
    def __str__(self):
        filename = self.file.name.split('/')[-1]
        return f"{self.event.title} - {filename}"