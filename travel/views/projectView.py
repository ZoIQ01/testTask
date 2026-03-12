from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import TravelProject, ProjectPlace
from ..serializers import TravelProjectSerializer, ProjectPlaceSerializer


class TravelProjectViewSet(viewsets.ModelViewSet):
    queryset = TravelProject.objects.all()
    serializer_class = TravelProjectSerializer

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()

        visited = project.places.filter(visited=True)
        if visited.exists():
            visited_titles = list(visited.values_list('place__title', flat=True))
            return Response(
                {
                    "error": "Cannot delete a project that has visited places.",
                    "visited_places": visited_titles,
                },
                status=status.HTTP_409_CONFLICT,
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get', 'post'], url_path='places', url_name='project-places')
    def project_places(self, request, pk=None):
        project = self.get_object()

        if request.method == 'GET':
            serializer = ProjectPlaceSerializer(project.places.all(), many=True)
            return Response(serializer.data)

        serializer = ProjectPlaceSerializer(data=request.data, context={'project': project})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='places/(?P<place_id>[^/.]+)', url_name='project-place-detail')
    def project_place_detail(self, request, pk=None, place_id=None):
        project = self.get_object()

        project_place = ProjectPlace.objects.filter(
            project=project, place__external_id=place_id
        ).first()

        if project_place is None:
            project_place = get_object_or_404(ProjectPlace, project=project, id=place_id)

        return Response(ProjectPlaceSerializer(project_place).data)
