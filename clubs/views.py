import json
import os
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.conf import settings
from brawl_job.data_fetcher.config import CLUBS, CLUBS_LIST_FILE
from brawl_job.data_fetcher.api_client import BrawlStarsAPIClient
from brawl_job.data_fetcher.data_processor import ClubDataProcessor
from brawl_job .main import iniciar_monitor_en_segundo_plano
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views import View
from datetime import datetime

# --- RUTAS DE ARCHIVOS ---
CLUB_DATA_FILE = Path(settings.BASE_DIR) / "brawl_job" / "data" / "clubs" / "laclubs.json"
LAST_UPDATE_FILE = Path(settings.BASE_DIR) / "brawl_job" / "data" / "last_update.json"
CLUBS_JSON_PATH = CLUBS_LIST_FILE
TOPS_FILE = Path(settings.BASE_DIR) / "brawl_job" / "data" / "members" / "tops.json"
# --- FIN RUTAS DE ARCHIVOS ---


def load_clubs():
    if CLUBS_JSON_PATH.exists():
        with open(CLUBS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_clubs(clubs_dict):
    with open(CLUBS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(clubs_dict, f, indent=2, ensure_ascii=False)

def main_page(request):
    return render(request, 'clubs/main_page.html', {})

def clubs_view(request):
    clubs_data = []
    fecha = None
    if CLUB_DATA_FILE.exists():
        try:
            with open(CLUB_DATA_FILE, "r", encoding="utf-8") as f:
                clubs_data = json.load(f)
        except Exception as e:
            print(f"ERROR leyendo {CLUB_DATA_FILE}: {e}")

    if LAST_UPDATE_FILE.exists():
        try:
            with open(LAST_UPDATE_FILE, "r", encoding="utf-8") as f:
                fecha = json.load(f)
        except Exception as e:
            print(f"ERROR leyendo {LAST_UPDATE_FILE}: {e}")

    context = {
        'clubs': clubs_data,
        'last_update': fecha
    }
    return render(request, 'clubs/laclubs.html', context)

def club_detail_view(request, club_tag):
    normalized_club_tag = club_tag.lstrip('#').upper()
    hashed_club_tag = '#' + normalized_club_tag.upper()

    api_client = BrawlStarsAPIClient()
    processor = ClubDataProcessor(api_client)

    global_rankings = api_client.fetch_rankings("clubs", "global")
    local_rankings_es = api_client.fetch_rankings("clubs", "ES")

    processor.process_single_club(club_tag, hashed_club_tag, global_rankings, local_rankings_es)

    json_path = os.path.join(settings.BASE_DIR, 'brawl_job','data', 'temp', 'club.json')
    fecha = None

    if not os.path.exists(json_path):
        context = {'error_message': f"Error interno: El archivo de datos de miembros no se encontró en '{json_path}'."}
        return render(request, 'clubs/club_detail.html', context)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            clubs_data = json.load(f)
    except Exception as e:
        context = {'error_message': f"Error interno leyendo members.json: {e}"}
        return render(request, 'clubs/club_detail.html', context)

    found_club = None
    if clubs_data.get("tag", "").upper() == hashed_club_tag:
        found_club = clubs_data

    if LAST_UPDATE_FILE.exists():
        try:
            with open(LAST_UPDATE_FILE, "r", encoding="utf-8") as f:
                fecha = json.load(f)
        except Exception as e:
            print(f"ERROR leyendo {LAST_UPDATE_FILE}: {e}")

    if found_club == None:
        context = {
        'error_message': "Este tag no pertenece a ningún club",
        'last_update': fecha
    }
    else:
        context = {
            'club': found_club,
            'last_update': fecha
        }
    return render(request, 'clubs/club_detail.html', context)

def tops_home(request):
    club_general_data = None
    fecha = None
    json_file_path = os.path.join(settings.BASE_DIR, 'brawl_job', 'data', 'social_media', 'lageneral.json')
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            club_general_data = json.load(f)
    except Exception as e:
        print(f"ERROR leyendo {json_file_path}: {e}")

    if LAST_UPDATE_FILE.exists():
        try:
            with open(LAST_UPDATE_FILE, "r", encoding="utf-8") as f:
                fecha = json.load(f)
        except Exception as e:
            print(f"ERROR leyendo {LAST_UPDATE_FILE}: {e}")

    context = {
        'club_general_data': club_general_data,
        'last_update': fecha
    }
    return render(request, 'clubs/tops_home.html', context)

def top_players_list(request, limit):
    top_n_players = []
    message = f"Cargando el Top {limit} de Jugadores..."
    fecha = None
    json_file_path = TOPS_FILE

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            all_players = json.load(f)
            top_n_players = all_players[:int(limit)]
            message = f"Mostrando el Top {limit} de Jugadores:"
    except Exception as e:
        message = f"ERROR cargando lista de jugadores: {e}"
        print(message)

    if LAST_UPDATE_FILE.exists():
        try:
            with open(LAST_UPDATE_FILE, "r", encoding="utf-8") as f:
                fecha = json.load(f)
        except Exception as e:
            print(f"ERROR leyendo {LAST_UPDATE_FILE}: {e}")

    context = {
        'limit': limit,
        'players': top_n_players,
        'message': message,
        'last_update': fecha
    }
    return render(request, 'clubs/top_players_list.html', context)

def member_detail_view(request, player_tag):
    api_client = BrawlStarsAPIClient()
    processor = ClubDataProcessor(api_client)
    processor.process_player_profile_data(player_tag)

    json_path = os.path.join(settings.BASE_DIR, 'brawl_job','data', 'temp', 'profile.json')
    fecha = None

    if not os.path.exists(json_path):
        context = {'error_message': f"Error interno: El archivo de datos de miembros no se encontró en '{json_path}'."}
        return render(request, 'clubs/member_detail.html', context)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            members_data = json.load(f)
    except Exception as e:
        context = {'error_message': f"Error interno leyendo members.json: {e}"}
        return render(request, 'clubs/member_detail.html', context)

    normalized_player_tag = player_tag.lstrip('#').upper()
    found_member = None
    if members_data.get("tag", "").upper() == normalized_player_tag:
        found_member = members_data

    if LAST_UPDATE_FILE.exists():
        try:
            with open(LAST_UPDATE_FILE, "r", encoding="utf-8") as f:
                fecha = json.load(f)
        except Exception as e:
            print(f"ERROR leyendo {LAST_UPDATE_FILE}: {e}")

    clubs_tags = ['#' + tag for tag in CLUBS.values()]
    with open(CLUBS_LIST_FILE, 'r', encoding="utf-8") as f:
        clubs = json.load(f)

    clubs_tags = []
    for name,tag in clubs.items():
        clubs_tags.append(tag)
        hashed_found_member_club_tag = '#' + members_data.get("club_tag", "")


    if found_member is None:
        context = {
            'error_message': "Este tag no pertenece a ningún jugador",
            'last_update': fecha
        }
    else:
        context = {
            'member': found_member,
            'last_update': fecha
        }

    return render(request, 'clubs/member_detail.html', context)

@login_required(login_url='/login/')
def admin_view(request):
    api_client = BrawlStarsAPIClient()
    processor = ClubDataProcessor(api_client)

    clubs_dict = load_clubs()
    console_msg = {"message": "Waiting for the request..."}  # Mensaje por defecto

    if request.method == 'POST':
        action = request.POST.get('action')
        opcion = request.POST.get('opcion')
        tag = request.POST.get('tag', '').strip()
        name = request.POST.get('name', '').strip()
        original_tag = request.POST.get('original_tag', '').strip()

        # Si console_msg ya tiene un status (ej. por el archivo), no lo sobrescribimos
        # a menos que sea el mensaje por defecto "Waiting for the request..."
        if console_msg.get("message") == "Waiting for the request..." or console_msg.get("status") != "error":
            if action in ['add', 'edit', 'delete', 'reload']:
                if action == 'add':
                    if name and tag:
                        if tag.upper() not in clubs_dict.values():
                            clubs_dict[name] = tag.upper()
                            save_clubs(clubs_dict)
                            console_msg = {"status": "success", "message": f"Club '{name}' añadido."}
                        else:
                            console_msg = {"status": "error", "message": f"El tag '{tag}' ya existe."}
                    else:
                        console_msg = {"status": "error", "message": "Nombre y tag son requeridos para añadir."}

                elif action == 'edit':
                    if name and tag and original_tag:
                        key_to_edit = None
                        for k, v in clubs_dict.items():
                            if v == original_tag.upper():
                                key_to_edit = k
                                break
                        if key_to_edit:
                            if tag.upper() != original_tag.upper() and tag.upper() in clubs_dict.values():
                                console_msg = {"status": "error", "message": f"El tag '{tag}' ya existe."}
                            else:
                                del clubs_dict[key_to_edit]
                                clubs_dict[name] = tag.upper()
                                save_clubs(clubs_dict)
                                console_msg = {"status": "success", "message": f"Club '{name}' editado."}
                        else:
                            console_msg = {"status": "error", "message": "Club a editar no encontrado."}
                    else:
                        console_msg = {"status": "error", "message": "Datos incompletos para editar."}

                elif action == 'delete':
                    if tag:
                        key_to_delete = None
                        for k, v in clubs_dict.items():
                            if v == tag.upper():
                                key_to_delete = k
                                break
                        if key_to_delete:
                            del clubs_dict[key_to_delete]
                            save_clubs(clubs_dict)
                            console_msg = {"status": "success", "message": f"Club con tag '{tag}' eliminado."}
                        else:
                            console_msg = {"status": "error", "message": "Club a eliminar no encontrado."}
                    else:
                        console_msg = {"status": "error", "message": "Tag requerido para eliminar."}

                elif action == 'reload':
                    try:
                        iniciar_monitor_en_segundo_plano()
                        console_msg = {"status": "success", "message": "Recarga completada correctamente."}
                    except Exception as e:
                        console_msg = {"status": "error", "message": f"Error en recarga: {e}"}

            elif opcion and tag:
                if opcion.lower() == "club":
                    try:
                        escaped_tag = tag.replace("#", "%23")
                        club_data = api_client._make_api_request(f"https://api.rnt.dev/alliances/get?tag={escaped_tag}")
                        console_msg = {"status": "success", "type": "club", "data": club_data}
                    except Exception as e:
                        console_msg = {"status": "error", "type": "club", "message": f"Error al buscar club {tag.upper()}: {e}"}

                elif opcion.lower() == "user":
                    try:
                        player_data = processor.process_player_profile_data(tag.upper())
                        console_msg = {"status": "success", "type": "user", "data": player_data}
                    except Exception as e:
                        console_msg = {"status": "error", "type": "user", "message": f"Error al buscar usuario {tag.upper()}: {e}"}
                else:
                    console_msg = {"status": "error", "message": f"Opción no válida: {opcion}"}
            else: # Esto se ejecuta si no hay action, ni opcion+tag, ni archivo
                # Si no se subió archivo y no hay acción/opción, el mensaje por defecto se mantiene
                console_msg = {"status": "info", "message": "Por favor, selecciona una opcion y proporciona un tag"}

        request.session['console_msg'] = console_msg
        return redirect('admin_view')

    clubs_list_for_template = [{"name": k, "tag": v} for k, v in clubs_dict.items()]
    console_msg = request.session.pop('console_msg', {"message": "Waiting for the request..."})

    fecha = None
    if LAST_UPDATE_FILE.exists():
        try:
            with open(LAST_UPDATE_FILE, "r", encoding="utf-8") as f:
                fecha = json.load(f)
        except Exception as e:
            print(f"ERROR leyendo {LAST_UPDATE_FILE}: {e}")
    else:
        fecha = {"date": datetime.now().strftime('%H:%M:%S (UTC) | %d/%m/%Y')}

    context = {
        "clubs_list": clubs_list_for_template,
        "console": json.dumps(console_msg, indent=2),
        "fecha": fecha
    }
    return render(request, "clubs/admin_panel.html", context)

class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('/login/')

    def get(self, request):
        logout(request)
        return redirect('/login/')
