from flask import Flask, render_template
from fetcher import fetch_aircraft_data
from database import update_database, get_all_aircraft
from visualizer import generate_map

app = Flask(__name__)

@app.route("/")
def home():
    # 1) Vai buscar os dados atuais ao dump1090
    data = fetch_aircraft_data()
    if data:
        update_database(data)

    # 2) Lê da base de dados local
    aircraft = get_all_aircraft()

    # 3) Gera o mapa com os aviões atuais
    generate_map(aircraft)

    # 4) Devolve o ficheiro HTML gerado
    return render_template("map.html")


if __name__ == "__main__":
    app.run(debug=True, host="192.168.100.3", port=5000)
