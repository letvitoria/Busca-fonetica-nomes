import sys
sys.path.insert(0, 'C:/Users/leticia.lvlf/Desktop/Busca-fonetica/Busca-fonetica-nomes')

# Start server in thread, make a POST, capture output
import threading
import urllib.request
import urllib.parse
import time

import os
from flask import Flask
from mvc_flask import FlaskMVC
from jinja2 import ChoiceLoader, FileSystemLoader

BASE_DIR = 'C:/Users/leticia.lvlf/Desktop/Busca-fonetica/Busca-fonetica-nomes'

app = Flask(__name__, static_url_path='/static', static_folder=BASE_DIR + '/app/static')
FlaskMVC(app)

original_loader = app.jinja_loader
views_path = BASE_DIR + '/app/views'
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(views_path),
    original_loader,
])

def run_server():
    app.run(debug=False, port=5555, use_reloader=False)

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(2)

print("=== Testando GET /csv-data ===")
try:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    resp = opener.open('http://127.0.0.1:5555/csv-data')
    print(f"Status: {resp.status}")
except Exception as e:
    print(f"Erro: {e}")

print("\n=== Testando POST /decidir ===")
try:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    data = urllib.parse.urlencode({'decisao': 'nao'}).encode()
    req = urllib.request.Request('http://127.0.0.1:5555/decidir', data=data, method='POST')
    resp = opener.open(req)
    print(f"Status final: {resp.status}, URL: {resp.url}")
except urllib.error.HTTPError as e:
    print(f"HTTPError {e.code}: {e.reason}")
    content = e.read().decode('utf-8', errors='replace')
    print(content[:2000])
except Exception as e:
    print(f"Erro: {type(e).__name__}: {e}")
