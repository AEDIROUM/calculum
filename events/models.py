from django.db import models


class Event(models.Model):
    title = models.CharField(
        max_length=200
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
    
    class Meta:
        ordering = ['-title']
    
    def __str__(self):
        return self.title
    
    
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