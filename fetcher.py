import requests

DUMP1090_URL = "https://ads-b.jcboliveira.xyz/dump1090/data/aircraft.json"

def fetch_aircraft_data():
    try:
        resp = requests.get(DUMP1090_URL, timeout=5)
        print("HTTP status:", resp.status_code)
        if resp.status_code == 200:
            data = resp.json()
            print("Nº de aviões recebidos:", len(data.get("aircraft", [])))
            return data
        else:
            print("Erro a obter dados do dump1090")
            return None
    except Exception as e:
        print("Erro na ligação ao dump1090:", e)
        return None
