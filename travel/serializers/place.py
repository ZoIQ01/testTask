from rest_framework import serializers
from ..models import Place, ProjectPlace
from ..utils import get_place_from_api
from ..const import MAX_PLACES_PER_PROJECT
from .note import NoteSerializer


class ProjectPlaceSerializer(serializers.ModelSerializer):
    external_id = serializers.CharField(source='place.external_id', read_only=True)
    title = serializers.CharField(source='place.title', read_only=True)
    image_url = serializers.URLField(source='place.image_url', read_only=True, allow_null=True)
    api_url = serializers.URLField(source='place.api_url', read_only=True, allow_null=True)

    notes = NoteSerializer(many=True, read_only=True)

    place_external_id = serializers.CharField(write_only=True)

    class Meta:
        model = ProjectPlace
        fields = ['id', 'external_id', 'title', 'image_url', 'api_url',
                  'visited', 'place_external_id', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'title', 'image_url', 'api_url', 'created_at', 'updated_at']

    def validate_place_external_id(self, value):
        project = self.context.get('project')

        if project and project.get_places_count() >= MAX_PLACES_PER_PROJECT:
            raise serializers.ValidationError(
                f"This project already has the maximum of {MAX_PLACES_PER_PROJECT} places."
            )

        place_data = get_place_from_api(value)
        if not place_data:
            raise serializers.ValidationError(
                f"No artwork with ID '{value}' was found in the Art Institute of Chicago API."
            )

        self._api_place_data = place_data

        if project and ProjectPlace.objects.filter(project=project, place__external_id=value).exists():
            raise serializers.ValidationError(f"Place '{value}' is already in this project.")

        return value

    def create(self, validated_data):
        external_id = validated_data.pop('place_external_id', None)
        project = self.context.get('project')

        if not project:
            raise serializers.ValidationError("Project context is required.")

        place, _ = Place.objects.get_or_create(
            external_id=external_id,
            defaults={
                'title': self._api_place_data.get('title', 'Unknown'),
                'image_url': self._api_place_data.get('image_url'),
                'api_url': self._api_place_data.get('api_url'),
            },
        )

        return ProjectPlace.objects.create(project=project, place=place, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('place_external_id', None)
        instance.visited = validated_data.get('visited', instance.visited)
        instance.save()
        return instance
