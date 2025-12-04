from flask import Flask, render_template, request
from datetime import datetime

from fetcher import fetch_aircraft_data
from database import update_database, get_all_aircraft
from visualizer import generate_map

app = Flask(__name__)


def _get_altitude(ac):
    """
    Mesmo critério que no visualizer: tenta vários campos de altitude.
    """
    candidates = [
        ac.get("alt_baro"),
        ac.get("altBaro"),
        ac.get("alt_geom"),
        ac.get("altGeom"),
        ac.get("altitude"),
        ac.get("alt"),
    ]

    for value in candidates:
        if value is None:
            continue
        if isinstance(value, str):
            if value.lower() == "ground":
                continue
            try:
                value = int(value)
            except ValueError:
                continue
        if isinstance(value, (int, float)):
            return int(value)
    return None


def _in_portugal_fir(lat, lon):
    """
    Filtro simples para 'espaço aéreo PT':
    caixa aproximada que cobre Portugal continental.
    """
    if lat is None or lon is None:
        return False

    LAT_MIN, LAT_MAX = 36.5, 42.2
    LON_MIN, LON_MAX = -10.2, -6.0

    return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX


def filtrar_aircraft(
    aircraft_list,
    so_espaco_aereo: bool = False,
    filtro_destino: str | None = None,
):
    """
    Aplica os filtros pedidos no enunciado:
      - 'so_espaco_aereo': aviões no espaço aéreo PT (bounding box + altitude>0)
      - 'filtro_destino': substring no campo 'flight' (voo / destino / companhia)
    """
    resultado = []

    if filtro_destino:
        filtro_destino = filtro_destino.strip().upper()

    for ac in aircraft_list:
        lat = ac.get("lat")
        lon = ac.get("lon")

        # filtro: aviões no espaço aéreo (Portugal)
        if so_espaco_aereo:
            if not _in_portugal_fir(lat, lon):
                continue
            alt = _get_altitude(ac)
            if alt is None or alt <= 0:
                continue

        # filtro: "destino" / voo (texto livre no campo flight)
        if filtro_destino:
            flight = (ac.get("flight") or "").strip().upper()
            if filtro_destino not in flight:
                continue

        resultado.append(ac)

    return resultado


@app.route("/")
def home():
    # 1) Vai buscar os dados atuais ao dump1090
    data = fetch_aircraft_data()
    if data is not None:
        update_database(data)
        print("[webapp] Base de dados atualizada com novos dados.")
    else:
        print("[webapp] Aviso: a usar últimos dados guardados (falha na atualização).")

    # 2) Lê da base de dados local
    aircraft = get_all_aircraft()
    print(f"[webapp] {len(aircraft)} aeronaves na BD antes de filtros.")

    # Estatísticas globais (antes de filtros)
    total_json = len(aircraft)
    total_with_pos = sum(
        1 for ac in aircraft if ac.get("lat") is not None and ac.get("lon") is not None
    )

    # 3) Ler filtros da query string
    in_airspace = request.args.get("in_airspace") == "on"
    dest = request.args.get("dest", "").strip() or None

    # 4) Aplicar filtros
    aircraft_filtrado = filtrar_aircraft(
        aircraft,
        so_espaco_aereo=in_airspace,
        filtro_destino=dest,
    )
    print(f"[webapp] {len(aircraft_filtrado)} aeronaves após filtros.")

    # Estatísticas da lista filtrada (o que está no mapa)
    filtered_total = len(aircraft_filtrado)
    filtered_with_pos = sum(
        1
        for ac in aircraft_filtrado
        if ac.get("lat") is not None and ac.get("lon") is not None
    )

    # 5) Gera o mapa com os aviões filtrados
    generate_map(aircraft_filtrado)

    # 6) Hora UTC
    timestamp_utc = datetime.utcnow().strftime("%H:%M:%S UTC")

    # 7) Devolve a página com painel de filtros + iframe do mapa
    return render_template(
        "map.html",
        in_airspace=in_airspace,
        dest=dest or "",
        total_json=total_json,
        total_with_pos=total_with_pos,
        filtered_total=filtered_total,
        filtered_with_pos=filtered_with_pos,
        last_update=timestamp_utc,
    )


@app.route("/map_inner")
def map_inner():
    """
    Serve o HTML gerado pelo Folium (só o mapa).
    """
    return render_template("map_inner.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
