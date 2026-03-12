from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import ProjectPlace
from ..serializers import ProjectPlaceSerializer, NoteSerializer


class ProjectPlaceViewSet(viewsets.ModelViewSet):
    queryset = ProjectPlace.objects.select_related('project', 'place').all()
    serializer_class = ProjectPlaceSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.kwargs.get('pk'):
            project_place = get_object_or_404(ProjectPlace, id=self.kwargs['pk'])
            context['project'] = project_place.project
        return context

    @action(detail=True, methods=['post'], url_path='mark-visited', url_name='mark-visited')
    def mark_visited(self, request, pk=None):
        project_place = self.get_object()
        project_place.visited = True
        project_place.save()
        return Response(self.get_serializer(project_place).data)

    @action(detail=True, methods=['post'], url_path='mark-unvisited', url_name='mark-unvisited')
    def mark_unvisited(self, request, pk=None):
        project_place = self.get_object()
        project_place.visited = False
        project_place.save()
        return Response(self.get_serializer(project_place).data)

    @action(detail=True, methods=['get', 'post'], url_path='notes', url_name='place-notes')
    def place_notes(self, request, pk=None):
        project_place = self.get_object()

        if request.method == 'GET':
            serializer = NoteSerializer(project_place.notes.all(), many=True)
            return Response(serializer.data)

        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_place=project_place)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
