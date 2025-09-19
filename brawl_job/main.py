# brawl_job/main.py
import time
import threading
import datetime
import sys
import os
import signal
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher.config import (
    CLUBS_OUTPUT_DIR,
    TIME_OUTPUT_DIR,
    CICLO,
    CLUBS_LIST_FILE,
    MAX_WORKERS_CLUB_FETCH,
)
from data_fetcher.api_client import BrawlStarsAPIClient
from data_fetcher.data_processor import ClubDataProcessor
from data_fetcher.utils import save_json

# Variables globales para controlar el monitor
monitor_thread = None
stop_event = None


def monitor_clubs_loop(stop_event: threading.Event):
    time.sleep(2)
    print("🔁 Monitor de clubes iniciado.")
    api_client = BrawlStarsAPIClient()
    processor = ClubDataProcessor(api_client)

    while not stop_event.is_set():
        api_client.clear_player_cache()
        print(f"\n⏳ Procesando clubs. Hora: {datetime.datetime.now().strftime('%H:%M:%S')}")

        global_rankings = api_client.fetch_rankings("clubs", "global")
        local_rankings_es = api_client.fetch_rankings("clubs", "ES")

        all_clubs_data = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_CLUB_FETCH) as executor:
            future_to_club = {
                executor.submit(processor.process_single_club, name, tag, global_rankings, local_rankings_es): (name, tag)
                for name, tag in clubs.items()
            }

            for future in as_completed(future_to_club):
                name, tag = future_to_club[future]
                try:
                    club_info = future.result()
                    if club_info:
                        all_clubs_data.append(club_info)
                except Exception as e:
                    print(f"❌ Error procesando club {name} ({tag}): {e}")

        if all_clubs_data:
            all_clubs_data.sort(key=lambda c: c.get("copas_totales", 0), reverse=True)
            save_json(all_clubs_data, "laclubs.json", CLUBS_OUTPUT_DIR)
            print("✅ Archivo 'laclubs.json' generado correctamente.")
            processor.generate_and_save_general_stats(all_clubs_data)
            processor.generate_and_save_all_members_data(all_clubs_data)
        else:
            print("⚠️ No se pudieron recuperar datos de ningún club.")

        last_update_data = {
            "date": datetime.datetime.now().strftime('%H:%M:%S (UTC) | %d/%m/%Y')
        }
        save_json(last_update_data, "last_update.json", TIME_OUTPUT_DIR)
        print("✅ Archivo 'last_update.json' generado correctamente.")
        print(f"\n\n⏱️CICLO FINALIZADO. Hora: {datetime.datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️ Esperando {round(CICLO / 60, 2)} minutos para el siguiente ciclo...\n")

        # Espera en intervalos de 1s, pero se puede cancelar si stop_event se activa
        for _ in range(CICLO):
            if stop_event.is_set():
                break
            time.sleep(1)


def iniciar_monitor_en_segundo_plano():
    with open(CLUBS_LIST_FILE, "r", encoding="utf-8") as f:
        global clubs
        clubs = json.load(f)
    global monitor_thread, stop_event

    # Si ya hay un monitor corriendo → detenerlo
    if monitor_thread and monitor_thread.is_alive():
        print("⛔ Deteniendo monitor anterior...")
        stop_event.set()
        monitor_thread.join()

    # Crear un nuevo evento y un nuevo hilo
    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_clubs_loop, args=(stop_event,), daemon=True)
    monitor_thread.start()
    print("✅ Nuevo monitor iniciado.")
    return monitor_thread


def main():
    iniciar_monitor_en_segundo_plano()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Monitor detenido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
