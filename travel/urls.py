from django.urls import path, include
from rest_framework.routers import DefaultRouter
from travel.views import TravelProjectViewSet, ProjectPlaceViewSet, NoteViewSet

router = DefaultRouter()
router.register(r'projects', TravelProjectViewSet, basename='project')
router.register(r'project-places', ProjectPlaceViewSet, basename='project-place')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    path('api/', include(router.urls)),
]
