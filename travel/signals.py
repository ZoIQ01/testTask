from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProjectPlace


@receiver(post_save, sender=ProjectPlace)
def update_project_completed(sender, instance, **kwargs):
    instance.project.sync_completed()
