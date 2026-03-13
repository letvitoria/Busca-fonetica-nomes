import os
from flask import Flask
from mvc_flask import FlaskMVC
from jinja2 import ChoiceLoader, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Adicione static_url_path e static_folder explicitamente
app = Flask(__name__, static_url_path='/static', static_folder='app/static')
FlaskMVC(app)

original_loader = app.jinja_loader  # salva o loader configurado pelo mvc_flask

views_path = os.path.join(BASE_DIR, "app", "views")
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(views_path),
    original_loader,
])

if __name__ == "__main__":
    app.run(debug=True, exclude_patterns=["*.csv"])