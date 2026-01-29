from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os


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


# Signal to delete old file when replacing with new one
@receiver(pre_save, sender=Media)
def delete_old_file_on_change(sender, instance, **kwargs):
    """
    Delete old file when a Media instance's file field is updated with a new file.
    """
    if not instance.pk:
        return  # New instance, no old file to delete
    
    try:
        old_instance = Media.objects.get(pk=instance.pk)
    except Media.DoesNotExist:
        return  # Instance doesn't exist yet, nothing to delete
    
    # Check if the file has changed
    if old_instance.file and old_instance.file != instance.file:
        # Delete the old file from storage
        if os.path.isfile(old_instance.file.path):
            os.remove(old_instance.file.path)


# Signal to delete file when Media instance is deleted
@receiver(post_delete, sender=Media)
def delete_file_on_delete(sender, instance, **kwargs):
    """
    Delete file from storage when Media instance is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)