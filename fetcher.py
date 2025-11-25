import json
import os
from typing import Optional, Dict, Any

import requests

from config import DUMP1090_URL, REQUEST_TIMEOUT, MAX_RETRIES, LAST_JSON_PATH


def _is_valid_aircraft_payload(data: Any) -> bool:
    """
    Verifica se o JSON tem a estrutura esperada:
    {'aircraft': [...] }
    """
    if not isinstance(data, dict):
        return False
    aircraft = data.get("aircraft")
    if not isinstance(aircraft, list):
        return False
    return True


def _save_raw_json(data: Dict[str, Any]) -> None:
    """Guarda o JSON em ficheiro (debug)."""
    try:
        os.makedirs(os.path.dirname(LAST_JSON_PATH), exist_ok=True)
        with open(LAST_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[fetcher] Aviso: não foi possível guardar o JSON bruto: {e}")


def fetch_aircraft_data() -> Optional[Dict[str, Any]]:
    """
    Vai buscar aircraft.json de forma robusta.
    - tenta várias vezes (MAX_RETRIES)
    - valida JSON
    - guarda o JSON bruto
    - trata erros de rede
    """
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[fetcher] Tentativa {attempt}/{MAX_RETRIES}...")

        try:
            resp = requests.get(DUMP1090_URL, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            print(f"[fetcher] Erro de ligação: {e}")
            continue

        if resp.status_code != 200:
            print(f"[fetcher] HTTP {resp.status_code}: erro ao obter aircraft.json")
            continue

        try:
            data = resp.json()
        except ValueError:
            print("[fetcher] Erro ao descodificar JSON")
            continue

        if not _is_valid_aircraft_payload(data):
            print("[fetcher] JSON inválido (falta 'aircraft' ou formato incorreto)")
            continue

        aircraft_list = data.get("aircraft", [])
        print(f"[fetcher] Sucesso → {len(aircraft_list)} aeronaves recebidas.")

        _save_raw_json(data)
        return data

    print("[fetcher] Falha após várias tentativas → sem dados.")
    return None
