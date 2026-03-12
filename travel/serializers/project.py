from rest_framework import serializers
from travel.models import TravelProject, Place, ProjectPlace
from travel.utils import get_place_from_api
from travel.const import MAX_PLACES_PER_PROJECT
from .place import ProjectPlaceSerializer


class TravelProjectSerializer(serializers.ModelSerializer):
    places = ProjectPlaceSerializer(many=True, read_only=True)
    places_count = serializers.SerializerMethodField()

    place_ids = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = TravelProject
        fields = ['id', 'name', 'description', 'start_date', 'completed',
                  'places', 'places_count', 'place_ids', 'created_at', 'updated_at']
        read_only_fields = ['id', 'completed', 'created_at', 'updated_at']

    def get_places_count(self, obj):
        return obj.get_places_count()

    def validate_place_ids(self, value):
        seen = set()
        dupes = []
        for v in value:
            if v in seen:
                dupes.append(v)
            else:
                seen.add(v)
        if dupes:
            raise serializers.ValidationError(f"Duplicate place IDs are not allowed: {', '.join(dupes)}.")

        if len(value) > MAX_PLACES_PER_PROJECT:
            raise serializers.ValidationError(
                f"A project can have at most {MAX_PLACES_PER_PROJECT} places. You provided {len(value)}."
            )

        self._cached_place_data = {}
        invalid_ids = []
        for external_id in value:
            place_data = get_place_from_api(external_id)
            if not place_data:
                invalid_ids.append(external_id)
            else:
                self._cached_place_data[external_id] = place_data

        if invalid_ids:
            raise serializers.ValidationError(
                f"The following IDs were not found in the Art Institute of Chicago API: {', '.join(invalid_ids)}."
            )

        return value

    def create(self, validated_data):
        place_ids = validated_data.pop('place_ids', [])
        project = TravelProject.objects.create(**validated_data)

        cached = getattr(self, '_cached_place_data', {})
        for external_id in place_ids:
            place_data = cached.get(external_id)
            if not place_data:
                continue

            place, _ = Place.objects.get_or_create(
                external_id=external_id,
                defaults={
                    'title': place_data.get('title', 'Unknown'),
                    'image_url': place_data.get('image_url'),
                    'api_url': place_data.get('api_url'),
                },
            )
            ProjectPlace.objects.get_or_create(project=project, place=place)

        return project
