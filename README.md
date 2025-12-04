**STAER Project**

Este projeto consiste num sistema que recolhe, trata e visualiza em tempo real a informação proveniente de radares secundários (Modo S / ADS-B) através do serviço dump1090.
A aplicação apresenta num mapa (OpenStreetMap) as aeronaves detetadas, com altitude, velocidade, rumo, identificação e outros dados relevantes.

**Funcionalidades Principais**

🔹 Recolha de dados (Modo S / ADS-B)
Dados obtidos de aircraft.json fornecido pelo dump1090.
Sistema de recolha robusto com:
⏱️ Timeouts automáticos.
🔁 Várias tentativas (retries).
🧪 Validação da estrutura JSON.
💾 Gravação do último JSON recebido (data/last_aircraft_raw.json).

🔹 Visualização em mapa (OpenStreetMap)
Mapa interativo gerado com Folium, incluindo:
✈️ Marcadores em formato avião.
🎨 Cores baseadas na altitude:
    🔴 Altitude alta.
    🟧 Altitude média.
    🟩 Altitude baixa.
    ⚪ Sem altitude.
ℹ️ Popup detalhado com:
    - ICAO.
    - Voo.
    - Altitude.
    - Velocidade.
    - Rumo.
ℹ️ Tooltip com identificador do voo.
🔄 Atualização automática a cada 10 segundos.

🔹 Estatísticas em overlay
Uma caixa no canto superior direito indica:
✈️ Aviões com posição válida.
📦 Total de aeronaves no JSON.
🕒 Hora da última atualização (UTC).

🔹 Webserver (Flask)
- Servido em:
    - http://127.0.0.1:5000/.
    - http://192.168.100.3:5000/.
- Renderização dinâmica e atualizada periodicamente.
- Mapas totalmente interativos.

🔹 Estrutura do Projeto
STAER/
├── __pycache__/
├── data/
│   ├── aircraft_db.json
│   ├── aircraft.json
│   └── last_aircraft_raw.json
├── templates/
│   └── map.html
├── app.py
├── config.py
├── database.py
├── fetcher.py
├── README.md
├── visualizer.py
├── webapp.py
├── venv/

🔹 Como executar 
Para arrancar o servidor Flask e visualizar o mapa em tempo real, segue estes passos:

1️⃣ Aceder ao servidor via SSH
- ssh staer@192.168.100.3
2️⃣ Entrar na pasta do projeto
- cd staer-app
3️⃣ Ativar o ambiente virtual
- source venv/bin/activate
4️⃣ Iniciar o servidor web (Flask)
- python3 webapp.py
5️⃣ Abrir o mapa no browser
- (http://127.0.0.1:5000/) ou (http://192.168.100.3:5000).