import folium
from branca.element import MacroElement
from jinja2 import Template
from datetime import datetime


class AircraftCounter(MacroElement):
    def __init__(self, with_pos, total, timestamp):
        super().__init__()
        self._name = "AircraftCounter"
        self.with_pos = with_pos
        self.total = total
        self.timestamp = timestamp
        self._template = Template("""
        {% macro html(this, kwargs) %}
        <div style="
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 9999;
            background-color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-family: Arial, sans-serif;
            font-size: 13px;
            box-shadow: 0 0 4px rgba(0,0,0,0.3);
        ">
            Aviões com posição: {{ this.with_pos }}<br>
            Total no JSON: {{ this.total }}<br>
            Última atualização: {{ this.timestamp }}
        </div>
        {% endmacro %}
        """)


class AutoRefresh(MacroElement):
    def __init__(self, seconds):
        super().__init__()
        self._name = "AutoRefresh"
        self.seconds = seconds
        self._template = Template("""
        {% macro html(this, kwargs) %}
        <script>
        setTimeout(function() {
            window.location.reload();
        }, {{ this.seconds * 1000 }});
        </script>
        {% endmacro %}
        """)


def _get_altitude(ac):
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


def generate_map(aircraft_list):
    # Centro aproximado no Norte de Portugal
    mapa = folium.Map(location=[41.1579, -8.6291], zoom_start=6)

    total = len(aircraft_list)
    with_pos = 0

    for ac in aircraft_list:
        lat = ac.get("lat")
        lon = ac.get("lon")
        if lat is None or lon is None:
            continue  # sem posição não aparece

        with_pos += 1

        # Altitude
        altitude = _get_altitude(ac)
        altitude_str = f"{altitude} ft" if altitude is not None else "Desconhecida"

        # Outros campos úteis
        icao = ac.get("hex", "N/A")
        flight = (ac.get("flight") or "").strip()
        speed = ac.get("gs") or ac.get("speed")  # normalmente 'gs' em dump1090
        track = ac.get("track")

              # Popup detalhado (versão formatada e bonita)
        flight_str = flight if flight else "N/A"
        speed_str = f"{int(speed)} kt" if speed is not None else "N/A"
        track_str = f"{int(track)}°" if track is not None else "N/A"

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; line-height: 1.4;">
            <b>ICAO:</b> {icao}<br>
            <b>Voo:</b> {flight_str}<br>
            <b>Altitude:</b> {altitude_str}<br>
            <b>Velocidade:</b> {speed_str}<br>
            <b>Rumo:</b> {track_str}
        </div>
        """

        # Cor do marcador em função da altitude
        if altitude is None:
            icon_color = "gray"
        elif altitude < 5000:
            icon_color = "green"
        elif altitude < 20000:
            icon_color = "orange"
        else:
            icon_color = "red"

        # Marcador com ícone de avião e popup formatado
        folium.Marker(
            [lat, lon],
            tooltip=f"{icao} {('(' + flight + ')') if flight else ''}",
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=icon_color, icon="plane", prefix="fa")
        ).add_to(mapa)


    # Timestamp da geração do mapa (UTC)
    timestamp = datetime.utcnow().strftime("%H:%M:%S UTC")

    # Caixa com contagem + hora
    mapa.get_root().add_child(AircraftCounter(with_pos, total, timestamp))
    # Refresh automático
    mapa.get_root().add_child(AutoRefresh(10))   # atualiza de 10 em 10 segundos

    mapa.save("templates/map.html")
