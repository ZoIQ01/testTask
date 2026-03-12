import requests
from .const import ARTIC_API_BASE, ARTIC_IMAGE_BASE_URL, API_REQUEST_TIMEOUT


def get_place_from_api(external_id):
    try:
        response = requests.get(f"{ARTIC_API_BASE}/artworks/{external_id}", timeout=API_REQUEST_TIMEOUT)
        if response.status_code != 200:
            return None

        data = response.json().get('data', {})
        image_id = data.get('image_id')

        return {
            'id': data.get('id'),
            'title': data.get('title', 'Unknown'),
            'image_url': f"{ARTIC_IMAGE_BASE_URL}/{image_id}/full/843,/0/default.jpg" if image_id else None,
            'api_url': data.get('_links', {}).get('self', {}).get('href'),
        }
    except requests.RequestException:
        return None


def search_places_in_api(query, limit=10):
    try:
        response = requests.get(
            f"{ARTIC_API_BASE}/artworks/search",
            params={'q': query, 'limit': limit},
            timeout=API_REQUEST_TIMEOUT,
        )
        if response.status_code != 200:
            return []

        results = []
        for item in response.json().get('data', []):
            image_id = item.get('image_id')
            results.append({
                'id': item.get('id'),
                'title': item.get('title', 'Unknown'),
                'image_url': f"{ARTIC_IMAGE_BASE_URL}/{image_id}/full/843,/0/default.jpg" if image_id else None,
                'api_url': item.get('_links', {}).get('self', {}).get('href'),
            })
        return results
    except requests.RequestException:
        return []
