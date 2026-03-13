from mvc_flask import Router

Router.get("/", "busca#executar")
Router.get("/listar", "busca#executar") #Aponta para o BuscaCentroller, não HomeController
Router.get("/csv-data", "home#csv_data")
Router.get("/relatorio", "home#relatorio")
Router.post("/decidir", "home#decidir")
Router.get("/listar", "home#listar")
# rota pra disparar a busca
Router.get("/executar", "busca#executar")