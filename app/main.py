from flask import flask
from mvc_flask import flaskMVC

def crate_app():
    app = flask(__name__, static_folder ="static", template_folder ="views")
    flaskMVC(app)
    return app