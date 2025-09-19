# brawl_job/data_fetcher/config.py
from pathlib import Path
import json

API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImMxN2JlYTAzLWZhMWUtNGM2MC1iZGQ4LTkyMzViODJiMzEwZSIsImlhdCI6MTc1ODEwMjUwMywic3ViIjoiZGV2ZWxvcGVyLzYxNTllM2Q2LWM5NWUtY2RlYy0yNmRjLTIzYzZjNThhZjZkOCIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiODQuNzYuMTU2LjU5IiwiOTAuMTYwLjUuMTEwIiwiNzIuNDQuNDguMTgyIl0sInR5cGUiOiJjbGllbnQifV19.oCd2TQgAGBgk7-yP58FLsJAVtNJvMYNPQdbRPYqeVc2huVaeTxIbTOo1cv7MN2wwOB-bdA9u9fZEZjGfDboAdg"
BASE_URL = "https://api.brawlstars.com/v1"
PROFILE_URL = "https://api.rnt.dev/profile?tag="
CLUB_URL = "https://api.rnt.dev/alliances/get?tag="

CLUBS_OUTPUT_DIR = Path("brawl_job/data/clubs")
RRSS_OUTPUT_DIR = Path("brawl_job/data/social_media")
MEMBERS_OUTPUT_DIR = Path("brawl_job/data/members")
TEMP_OUTPUT_DIR = Path("brawl_job/data/temp")
TIME_OUTPUT_DIR = Path("brawl_job/data")
CLUBS_LIST_FILE = Path("brawl_job/data/clubs_list.json")
CICLO = 7200

with open(CLUBS_LIST_FILE, "r", encoding="utf-8") as f:
    CLUBS = json.load(f)

ROLE_TRANSLATIONS = {
    "vicePresident": "VicePresidente",
    "senior": "Veterano",
    "member": "Miembro",
    "president": "Presidente"
}

COLORS_TRANSLATIONS = {
    43000000: "#ffffff",
    43000001: "#44C76E",
    43000002: "#E3D062",
    43000003: "#D8F211",
    43000004: "#E39434",
    43000005: "#DE9A47",
    43000006: "#D97423",
    43000007:"#D667AD",
    43000008: "#90D5FF",
    43000009:"#3C60CF",
    43000010:"#B01ED4",
    43000011:"#1DDB66"
}

ROLE_TRANSLATIONS_NUMBERS = {
    3: "Veterano",
    1: "Miembro",
    2: "Presidente",
    4: "VicePresidente"
}

MAX_WORKERS_PLAYER_FETCH = 10
MAX_WORKERS_CLUB_FETCH = max(1, len(CLUBS) // 4)

# Crear directorios si no existen
for directory in [CLUBS_OUTPUT_DIR, RRSS_OUTPUT_DIR, MEMBERS_OUTPUT_DIR, TEMP_OUTPUT_DIR, TIME_OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

if not API_TOKEN:
    print("❌ ERROR: No se pudo cargar el token de la API de Brawl Stars. Comprueba tu archivo .env")
    exit(1)