from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from .models import TravelProject, Place, ProjectPlace

FAKE_PLACE_DATA = {
    'id': '27992',
    'title': 'La Grande Jatte',
    'image_url': None,
    'api_url': None,
}


class MainFeaturesTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_project_and_add_place(self):
        response = self.client.post('/api/projects/', {'name': 'My Trip'}, format='json')
        self.assertEqual(response.status_code, 201)
        project_id = response.data['id']

        with patch('travel.serializers.place.get_place_from_api', return_value=FAKE_PLACE_DATA):
            response = self.client.post(
                f'/api/projects/{project_id}/places/',
                {'place_external_id': '27992'},
                format='json',
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['external_id'], '27992')
        self.assertEqual(response.data['title'], 'La Grande Jatte')
        self.assertFalse(response.data['visited'])

    def test_marking_all_places_visited_completes_the_project(self):
        project = TravelProject.objects.create(name='Quick Trip')
        place = Place.objects.create(external_id='111', title='Some Artwork')
        project_place = ProjectPlace.objects.create(project=project, place=place)

        response = self.client.post(f'/api/project-places/{project_place.id}/mark-visited/')
        self.assertEqual(response.status_code, 200)

        project = TravelProject.objects.get(id=project.id)
        self.assertTrue(project.completed)

    def test_cannot_delete_project_with_visited_places(self):
        project = TravelProject.objects.create(name='Visited Trip')
        place = Place.objects.create(external_id='222', title='Some Artwork')
        ProjectPlace.objects.create(project=project, place=place, visited=True)

        response = self.client.delete(f'/api/projects/{project.id}/')

        self.assertEqual(response.status_code, 409)
        self.assertTrue(TravelProject.objects.filter(id=project.id).exists())
