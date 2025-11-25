# config.py

# URL de origem dos dados dump1090 (Mode S / ADS-B)
DUMP1090_URL = "https://ads-b.jcboliveira.xyz/dump1090/data/aircraft.json"

# Timeout máximo para a ligação HTTP (segundos)
REQUEST_TIMEOUT = 5

# Nº máximo de tentativas em caso de erro (rede / timeout / HTTP != 200)
MAX_RETRIES = 3

# Ficheiro opcional para guardar o último JSON recebido (para debug)
LAST_JSON_PATH = "data/last_aircraft_raw.json"
