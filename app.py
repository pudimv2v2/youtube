from flask import Flask, request, render_template, redirect, jsonify
import os
import json
import uuid
import datetime
import requests

app = Flask(__name__)
LOG_FILE = 'log.json'

@app.route('/')
def index():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    pass
    return render_template('index.html', logs=logs)

@app.route('/gerar_link', methods=['POST'])
def gerar_link():
    data = request.get_json()
    youtube_url = data.get('youtube_url')
    if not youtube_url or "youtube.com/watch?v=" not in youtube_url:
        return jsonify({'erro': 'URL inválida'}), 400

    tracking_id = uuid.uuid4().hex
    return jsonify({'link': f'{request.host_url}r/{tracking_id}?v={youtube_url}'})

@app.route('/r/<tracking_id>')
def rastrear(tracking_id):
    youtube_url = request.args.get('v')
    ip_raw = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip = ip_raw.split(',')[0].strip()  # Usa apenas o primeiro IP da lista

    try:
        location_data = requests.get(f"http://ip-api.com/json/{ip}").json()
        cidade = location_data.get('city', 'Cidade Desconhecida')
        regiao = location_data.get('regionName', 'Região Desconhecida')
        pais = location_data.get('country', 'País Desconhecido')
        local = f"{cidade}, {regiao} - {pais}"
    except Exception:
        local = "Desconhecida"

    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_address": ip_raw,
        "location": local,
        "tracking_id": tracking_id
    }

    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    return redirect(youtube_url)

@app.route('/get_logs')
def get_logs():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    pass
    return jsonify(logs)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
