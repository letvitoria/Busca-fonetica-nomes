from flask import render_template

class HomeController:
    def index(self):
        return render_template("index.html")

    def listar(self):
        return render_template("listar.html")