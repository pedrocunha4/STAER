from fetcher import fetch_aircraft_data
from database import update_database

if __name__ == "__main__":
    data = fetch_aircraft_data()
    if data:
        update_database(data)
        print("Base de dados atualizada com sucesso!")
    else:
        print("Não foram obtidos dados.")
