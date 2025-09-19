# brawl_job/data_fetcher/data_processor.py
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

from data_fetcher.api_client import BrawlStarsAPIClient
from data_fetcher.models import Club, Player, GeneralStats, PlayerProfile
from data_fetcher.config import MAX_WORKERS_PLAYER_FETCH, ROLE_TRANSLATIONS, COLORS_TRANSLATIONS, RRSS_OUTPUT_DIR, MEMBERS_OUTPUT_DIR, TEMP_OUTPUT_DIR, ROLE_TRANSLATIONS_NUMBERS
from data_fetcher.utils import save_json

class ClubDataProcessor:
    def __init__(self, api_client: BrawlStarsAPIClient):
        self.api_client = api_client

    def process_single_club(self, name: str, tag: str, global_rankings: List[Dict[str, Any]], local_rankings_es: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        print(f"📡 Procesando club: {name} ({tag})...")
        club_raw_data = self.api_client.fetch_club_data(tag)
        if not club_raw_data:
            print(f"⚠️  Fallo obteniendo datos de '{name}'.")
            return None

        club = Club(club_raw_data)

        members_detailed_info_unsorted: List[Player] = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_PLAYER_FETCH) as executor:
            future_to_member_summary = {
                executor.submit(self.api_client.fetch_player_data, member_summary.get("tag")): member_summary
                for member_summary in club.members_summary
            }

            for future in as_completed(future_to_member_summary):
                member_summary = future_to_member_summary[future]
                player_raw_data = future.result()
                if player_raw_data:
                    player = Player(player_raw_data)
                    player.role = ROLE_TRANSLATIONS.get(member_summary.get("role"), member_summary.get("role"))
                    members_detailed_info_unsorted.append(player)
                else:
                    player = Player({
                        "tag": member_summary.get("tag"),
                        "name": member_summary.get("name"),
                        "trophies": member_summary.get("trophies"),
                        "role": member_summary.get("role"),
                        "icon": member_summary.get("icon")
                    })
                    members_detailed_info_unsorted.append(player)

        club.members_detailed = sorted(members_detailed_info_unsorted, key=lambda m: m.trophies, reverse=True)
        for idx, member in enumerate(club.members_detailed):
            member.top_rank = idx + 1

        club.top_global = next((entry.get("rank", 0) for entry in global_rankings if entry.get("tag") == tag), 0)
        club.top_local_es = next((entry.get("rank", 0) for entry in local_rankings_es if entry.get("tag") == tag), 0)

        # Guardar en JSON
        save_json(club.to_dict(), f"club.json", TEMP_OUTPUT_DIR)

        print(f"✅ Club '{name}' procesado correctamente.")
        return club.to_dict()

    def generate_and_save_general_stats(self, all_clubs_data: List[Dict[str, Any]]):
        if not all_clubs_data:
            print("⚠️ No hay datos para generar estadísticas generales.")
            return
        general_stats = GeneralStats(all_clubs_data)
        save_json(general_stats.to_dict(), "lageneral.json", RRSS_OUTPUT_DIR)
        print("✅ Archivo 'lageneral.json' generado correctamente.")

    def generate_and_save_all_members_data(self, all_clubs_data: List[Dict[str, Any]]):
        if not all_clubs_data:
            print("⚠️ No hay datos de clubes para generar el archivo de miembros.")
            return

        all_members_list = []
        for club_data in all_clubs_data:
            club_name = club_data.get("nombre")
            club_tag = club_data.get("tag")
            club_icon = club_data.get("club_icon")
            for member_data in club_data.get("miembros", []):
                member_info = {
                    "nombre": member_data.get("nombre"),
                    "tag": member_data.get("tag"),
                    "copas": member_data.get("copas"),
                    "rol": member_data.get("rol"),
                    "icono": member_data.get("icono"),
                    "club_nombre": club_name,
                    "club_tag": club_tag,
                    "club_icono": club_icon
                }
                all_members_list.append(member_info)

        all_members_list.sort(key=lambda m: m.get("copas", 0), reverse=True)

        all_members_with_top_first = []
        for idx, member in enumerate(all_members_list, start=1):
            member_with_top = {"top": idx}
            member_with_top.update(member)
            all_members_with_top_first.append(member_with_top)

        save_json(all_members_with_top_first, "tops.json", MEMBERS_OUTPUT_DIR)
        print("✅ Archivo 'tops.json' generado correctamente.")

    def process_player_profile_data(self, player_tag: str):
        print(f"📡 Procesando perfil de jugador: {player_tag}...")

        # Obtener datos perfil API rnt.dev
        player_raw_data = self.api_client.fetch_player_profile_data(player_tag)
        if not player_raw_data or not player_raw_data.get("ok"):
            print(f"⚠️ Fallo obteniendo datos de perfil para '{player_tag}'. Asegúrate de que el tag es correcto y existe.")
            return

        # Crear objeto PlayerProfile con rol club obtenido
        player_profile = PlayerProfile(player_raw_data)

        # Agregar los brawlers directamente al objeto
        player_profile.brawlers = player_raw_data["result"].get("brawlers", [])

        # Obtener rol en el club
        data = self.api_client.fetch_club_role_data(player_profile.club_tag)
        members = data["result"]["members"]
        for member in members:
            if (member["tag"]["tag"]).replace('#', '') == player_profile.tag:
                player_profile.club_rol = ROLE_TRANSLATIONS_NUMBERS.get(member["role"], member["role"])

        clean_tag = player_profile.tag.replace("#", "")

        # Ajustes extra
        player_profile.ranked_actual_liga += 58000000
        player_profile.ranked_record_liga += 58000000
        player_profile.name_color = COLORS_TRANSLATIONS.get(player_profile.name_color, player_profile.name_color)

        # Guardar en JSON
        save_json(player_profile.to_dict(), f"profile.json", TEMP_OUTPUT_DIR)
        print(f"✅ Perfil de jugador '{player_profile.name}' ({player_profile.tag}) guardado en 'profile.json'.")

        return player_raw_data
