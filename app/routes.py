from mvc_flask import Router

Router.get("/", "home#index")
Router.get("/listar", "home#listar")
Router.get("/csv", "home#csv")
Router.get("/csv-data", "home#csv_data")
Router.get("/relatorio", "home#relatorio")
 
# rota pra disparar a busca
Router.get("/executar", "busca#executar")