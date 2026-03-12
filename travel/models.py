from django.db import models


class TravelProject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def sync_completed(self):
        has_places = self.places.exists()
        all_visited = not self.places.filter(visited=False).exists()
        self.completed = has_places and all_visited
        self.save(update_fields=['completed'])

    def get_places_count(self):
        return self.places.count()

    class Meta:
        ordering = ['-created_at']


class Place(models.Model):
    external_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    api_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class ProjectPlace(models.Model):
    project = models.ForeignKey(TravelProject, on_delete=models.CASCADE, related_name='places')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='projects')
    visited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'place')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.project.name} - {self.place.title}"


class Note(models.Model):
    project_place = models.ForeignKey(ProjectPlace, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for {self.project_place}"

    class Meta:
        ordering = ['-updated_at']
