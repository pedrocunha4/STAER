import folium
from branca.element import MacroElement
from jinja2 import Template

class AircraftCounter(MacroElement):
    def __init__(self, with_pos, total):
        super().__init__()
        self._name = "AircraftCounter"
        self.with_pos = with_pos
        self.total = total
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
            Total no JSON: {{ this.total }}
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
    mapa = folium.Map(location=[41.1579, -8.6291], zoom_start=6)

    total = len(aircraft_list)
    with_pos = 0

    for ac in aircraft_list:
        lat = ac.get("lat")
        lon = ac.get("lon")
        if lat is None or lon is None:
            continue  # sem posição não aparece

        with_pos += 1

        altitude = _get_altitude(ac)
        altitude_str = f"{altitude} ft" if altitude is not None else "Desconhecida"

        icao = ac.get("hex", "N/A")
        flight = ac.get("flight", "").strip() if ac.get("flight") else ""

        popup_parts = [f"ICAO: {icao}"]
        if flight:
            popup_parts.append(f"Voo: {flight}")
        popup_parts.append(f"Altitude: {altitude_str}")
        popup_html = "<br>".join(popup_parts)

        folium.Marker(
            [lat, lon],
            tooltip=f"{icao} {('('+flight+')') if flight else ''}",
            popup=popup_html,
        ).add_to(mapa)

    mapa.get_root().add_child(AircraftCounter(with_pos, total))
    mapa.get_root().add_child(AutoRefresh(10))   # atualiza de 10 em 10 segundos

    mapa.save("templates/map.html")
