from mvc_flask import Router

Router.get("/", "home#index")
Router.get("/listar", "home#listar")
 
# rota pra disparar a busca
Router.get("/executar", "busca#executar")