import requests
from django.core.management.base import BaseCommand, CommandError
from travel.models import Place, TravelProject, ProjectPlace
from travel.utils import get_place_from_api
from travel.const import ARTIC_API_BASE, API_REQUEST_TIMEOUT


class Command(BaseCommand):
    help = 'Import artworks from Art Institute of Chicago API'

    def add_arguments(self, parser):
        parser.add_argument(
            'query',
            type=str,
            nargs='?',
            default='chicago',
            help='Search query for artworks (default: "chicago")'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of artworks to import (default: 10)'
        )
        parser.add_argument(
            '--project',
            type=int,
            help='Project ID to add imported artworks to'
        )

    def handle(self, *args, **options):
        query = options['query']
        limit = options['limit']
        project_id = options['project']

        self.stdout.write(self.style.SUCCESS(f'🔍 Searching for "{query}" on Art Institute API...'))

        try:
            url = f'{ARTIC_API_BASE}/artworks/search'
            params = {'q': query, 'limit': limit}
            response = requests.get(url, params=params, timeout=API_REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json().get('data', [])
            
            if not data:
                self.stdout.write(self.style.WARNING(f'No artworks found for "{query}"'))
                return

            self.stdout.write(self.style.SUCCESS(f'✓ Found {len(data)} artworks'))
            
            project = None
            if project_id:
                try:
                    project = TravelProject.objects.get(id=project_id)
                    self.stdout.write(self.style.SUCCESS(f'✓ Adding artworks to project: {project.name}'))
                except TravelProject.DoesNotExist:
                    raise CommandError(f'Project with ID {project_id} not found')

            imported_count = 0
            skipped_count = 0

            for item in data:
                external_id = str(item.get('id'))
                title = item.get('title', 'Unknown')

                place_data = get_place_from_api(external_id)
                if not place_data:
                    self.stdout.write(self.style.WARNING(f'Skipped: {title} (ID: {external_id}) - Could not fetch details'))
                    skipped_count += 1
                    continue

                place, created = Place.objects.get_or_create(
                    external_id=external_id,
                    defaults={
                        'title': place_data.get('title', 'Unknown'),
                        'image_url': place_data.get('image_url'),
                        'api_url': place_data.get('api_url'),
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created: {place.title}'))
                    imported_count += 1
                else:
                    self.stdout.write(f'  Already exists: {place.title}')
                    skipped_count += 1

                if project:
                    project_place, project_created = ProjectPlace.objects.get_or_create(
                        project=project,
                        place=place
                    )
                    if project_created:
                        self.stdout.write(f'    → Added to project: {project.name}')

            self.stdout.write(self.style.SUCCESS(f'\n✓ Import complete!'))
            self.stdout.write(f'  Imported: {imported_count}')
            self.stdout.write(f'  Skipped: {skipped_count}')

        except requests.exceptions.RequestException as e:
            raise CommandError(f'API request failed: {str(e)}')
        except Exception as e:
            raise CommandError(f'Import failed: {str(e)}')
