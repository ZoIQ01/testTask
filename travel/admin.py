from django.contrib import admin
from .models import TravelProject, Place, ProjectPlace, Note


@admin.register(TravelProject)
class TravelProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'get_places_count', 'completed', 'created_at']
    list_filter = ['created_at', 'start_date']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'external_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'external_id']
    readonly_fields = ['created_at', 'external_id']


@admin.register(ProjectPlace)
class ProjectPlaceAdmin(admin.ModelAdmin):
    list_display = ['project', 'place', 'visited', 'created_at']
    list_filter = ['visited', 'created_at', 'project']
    search_fields = ['project__name', 'place__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['project_place', 'content_preview', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['project_place__place__title', 'content']
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
