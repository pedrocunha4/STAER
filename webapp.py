from flask import Flask, render_template
from fetcher import fetch_aircraft_data
from database import update_database, get_all_aircraft
from visualizer import generate_map

app = Flask(__name__)

@app.route("/")
def home():
    # 1) Vai buscar os dados atuais ao dump1090
    data = fetch_aircraft_data()
    if data is not None:
        # Atualiza a BD com dados frescos
        update_database(data)
        print("[webapp] Base de dados atualizada com novos dados.")
    else:
        # Mantém dados anteriores na BD
        print("[webapp] Aviso: a usar últimos dados guardados (falha na atualização).")

    # 2) Lê da base de dados local
    aircraft = get_all_aircraft()
    print(f"[webapp] A mostrar {len(aircraft)} aeronaves no mapa.")

    # 3) Gera o mapa com os aviões atuais
    generate_map(aircraft)

    # 4) Devolve o ficheiro HTML gerado
    return render_template("map.html")


if __name__ == "__main__":
    # '0.0.0.0' deixa o serviço acessível mesmo que o IP da máquina mude
    app.run(debug=True, host="0.0.0.0", port=5000)
