# brawl_job/data_fetcher/models.py
from typing import List, Dict, Any, Optional
from .config import ROLE_TRANSLATIONS

class Player:
    def __init__(self, data: Dict[str, Any]):
        self.tag: str = data.get("tag", "")
        self.name: str = data.get("name", "")
        self.trophies: int = data.get("trophies", 0)
        self.role: str = ROLE_TRANSLATIONS.get(data.get("role"), data.get("role"))
        self.icon_id: Optional[int] = data.get("icon", {}).get("id")
        self.top_rank: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "top": self.top_rank,
            "nombre": self.name,
            "tag": self.tag,
            "copas": self.trophies,
            "rol": self.role,
            "icono": self.icon_id,
        }

class Club:
    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get("name", "")
        self.tag: str = data.get("tag", "")
        self.description: str = data.get("description", "").replace('"', "")
        self.badge_id: Optional[int] = data.get("badgeId")
        self.total_trophies: int = data.get("trophies", 0)
        self.required_trophies: int = data.get("requiredTrophies", 0)
        self.type: str = data.get("type", "")
        self.members_summary: List[Dict[str, Any]] = data.get("members", [])
        self.members_detailed: List[Player] = []
        self.top_global: int = 0
        self.top_local_es: int = 0

    @property
    def num_members(self) -> int:
        return len(self.members_summary)

    @property
    def president_name(self) -> Optional[str]:
        return next((m["name"] for m in self.members_summary if m.get("role") == "president"), None)

    @property
    def num_veterans(self) -> int:
        return sum(1 for m in self.members_summary if m.get("role") == "senior")

    @property
    def num_vicepresidents(self) -> int:
        return sum(1 for m in self.members_summary if m.get("role") == "vicePresident")

    @property
    def avg_trophies(self) -> float:
        return self.total_trophies // self.num_members if self.num_members else 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.name,
            "tag": self.tag,
            "descripcion": self.description,
            "club_icon": self.badge_id,
            "copas_totales": self.total_trophies,
            "n_miembros": self.num_members,
            "requiredTrophies": self.required_trophies,
            "type": self.type,
            "presidente": self.president_name,
            "num_veterans": self.num_veterans,
            "num_vicepresidents": self.num_vicepresidents,
            "media_copas": self.avg_trophies,
            "top_global": self.top_global,
            "top_local_ES": self.top_local_es,
            "miembros": [member.to_dict() for member in self.members_detailed],
        }

class GeneralStats:
    def __init__(self, all_clubs_data: List[Dict[str, Any]]):
        self.num_clubs: int = len(all_clubs_data)
        self.total_trophies: int = sum(club.get("copas_totales", 0) for club in all_clubs_data)
        self.total_members: int = sum(club.get("n_miembros", 0) for club in all_clubs_data)
        self.avg_trophies: float = self.total_trophies / self.num_clubs if self.num_clubs else 0
        self.discord: int = 6976
        self.online: int = 243
        self.tiktok: int = 101
        self.twitter: int = 1371

    def to_dict(self) -> Dict[str, Any]:
        return {
            "numero_de_clubs": self.num_clubs,
            "total_de_copas": self.total_trophies,
            "total_de_miembros": self.total_members,
            "media_de_copas": round(self.avg_trophies, 0),
            "discord": self.discord,
            "online": self.online,
            "tiktok": self.tiktok,
            "twitter": self.twitter,
        }

class PlayerProfile:
    def __init__(self, data: Dict[str, Any], club_rol: Optional[int] = None):
        result = data.get("result", {})
        self.tag: str = result.get("account_tag", {}).get("tag", "").replace("#", "")
        self.name: str = result.get("name", "")
        self.name_color: int = result.get("name_color", 0)

        stats_dict = {s.get("name"): s.get("value") for s in result.get("stats", [])}

        self.trophies: int = stats_dict.get("Trophies", 0)
        self.highest_trophies: int = stats_dict.get("HighestTrophies", 0)
        self.brawler_count: int = result.get("brawler_count", 0)
        self.sd_wins: int = stats_dict.get("SoloVictories", 0) + stats_dict.get("DuoVictories", 0)
        self.victories_3v3: int = stats_dict.get("3v3Victories", 0)
        self.icon_id: int = result.get("profile_avatar", 0)

        club_info = result.get("alliance", {})
        self.club_tag: Optional[str] = club_info.get("id", {}).get("tag", "").replace("#", "") if club_info else None
        self.club_name: Optional[str] = club_info.get("name") if club_info else None
        self.club_rol: Optional[str] = club_rol
        self.club_icon: Optional[int] = club_info.get("badge") if club_info else None

        self.ranked_actual_pts: Optional[int] = stats_dict.get("CurrentRankedPoints")
        self.ranked_actual_liga: str = stats_dict.get("CurrentRanked") or ""
        self.ranked_record_pts: Optional[int] = stats_dict.get("HighestRankedPoints")
        self.ranked_record_liga: str = stats_dict.get("HighestRanked") or ""
        self.records_pts: Optional[int] = stats_dict.get("RecordPoints")
        self.records_liga: Optional[int] = stats_dict.get("RecordLevel")

        self.max_winstreak: int = result.get("max_winstreak", 0)
        self.winstreak_brawler: int = result.get("winstreak_brawler")

        battle_card_data = result.get("battle_card", {})
        self.battle_card: Dict[str, Any] = {
            "favorite_skin": battle_card_data.get("favorite_skin", 0),
            "first_profile_avatar": battle_card_data.get("first_profile_avatar", 0),
            "second_profile_avatar": battle_card_data.get("second_profile_avatar", 0),
            "battle_card_emote": battle_card_data.get("battle_card_emote", 0),
            "title": battle_card_data.get("title", 0)
        }

        self.brawlers: List[Dict[str, Any]] = result.get("brawlers", [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "name": self.name,
            "name_color": self.name_color,
            "trophies": self.trophies,
            "highest_trophies": self.highest_trophies,
            "brawler_count": self.brawler_count,
            "sd_wins": self.sd_wins,
            "victories_3v3": self.victories_3v3,
            "icon_id": self.icon_id,
            "club_tag": self.club_tag,
            "club_name": self.club_name,
            "club_rol": self.club_rol,
            "club_icon": self.club_icon,
            "ranked_actual_pts": self.ranked_actual_pts,
            "ranked_actual_liga": self.ranked_actual_liga,
            "ranked_record_pts": self.ranked_record_pts,
            "ranked_record_liga": self.ranked_record_liga,
            "records_pts": self.records_pts,
            "records_liga": self.records_liga,
            "max_winstreak": self.max_winstreak,
            "winstreak_brawler": self.winstreak_brawler,
            "brawlers": self.brawlers,
            "battle_card": self.battle_card
        }