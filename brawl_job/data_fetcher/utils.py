# brawl_job/data_fetcher/utils.py
import json
import os
from typing import Dict, List, Any


def save_json(data: Dict[str, Any] | List[Dict[str, Any]], filename: str, output):
    """
    Guarda datos en un archivo JSON en el directorio de salida.
    """
    file_path = output / filename
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"❌ ERROR al guardar '{file_path}': {e}")