# brawl_job/data_fetcher/api_client.py
import requests
import time
from typing import Dict, Any, Optional, List
from data_fetcher.config import API_TOKEN, BASE_URL, PROFILE_URL, CLUB_URL

class BrawlStarsAPIClient:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {API_TOKEN}"}
        self.player_data_cache: Dict[str, Dict[str, Any]] = {}

    def _make_api_request(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Filtramos el 429
            if e.response is not None and e.response.status_code == 429:
                return None  # no imprimimos nada
            print(f"❌ Error HTTP en la solicitud para {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la solicitud para {url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado al hacer la solicitud a {url}: {e}")
            return None

    def fetch_club_data(self, tag: str) -> Optional[Dict[str, Any]]:
        escaped_tag = tag.replace("#", "%23")
        return self._make_api_request(f"{BASE_URL}/clubs/{escaped_tag}")

    def fetch_player_data(self, player_tag: str) -> Optional[Dict[str, Any]]:
        if player_tag in self.player_data_cache:
            return self.player_data_cache[player_tag]

        escaped_tag = player_tag.replace("#", "%23")
        data = self._make_api_request(f"{BASE_URL}/players/{escaped_tag}")
        if data:
            self.player_data_cache[player_tag] = data
        return data

    def fetch_player_profile_data(self, player_tag: str) -> Optional[Dict[str, Any]]:
        clean_tag = player_tag.replace("#", "")
        url = f"{PROFILE_URL}{clean_tag}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la solicitud a la API de perfil ({url}): {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado al hacer la solicitud a la API de perfil ({url}): {e}")
            return None

    def fetch_club_role_data(self, club_tag: str) -> Optional[Dict[str, Any]]:
        clean_tag = club_tag.replace("#", "")
        url = f"{CLUB_URL}{clean_tag}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la solicitud a la API de perfil ({url}): {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado al hacer la solicitud a la API de perfil ({url}): {e}")
            return None

    def fetch_rankings(self, ranking_type: str, country_code: str = "global") -> List[Dict[str, Any]]:
        url = f"{BASE_URL}/rankings/{country_code}/{ranking_type}" if country_code != "global" else f"{BASE_URL}/rankings/global/{ranking_type}"
        data = self._make_api_request(url)
        return data.get("items", []) if data else []

    def clear_player_cache(self):
        self.player_data_cache = {}
        print("Caché de jugadores limpiada.")