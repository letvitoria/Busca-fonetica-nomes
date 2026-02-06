# import sqlite3
# import os

# #Primeiro definir a pasta correta onde está meu banco de dados

# DIR = os.path.dirname(os.path.abspath(__file__))
# # .. Para chegar na raiz do projeto Busca-fonetica-nomes
# #
# #Definindo o caminho do banco de dados:
# DB_PATH = os.path.join(DIR, "bases", "ro_civil.db")

# #Conectar-se ao DB
# def conectar_db():
#     try:
#         conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#         #Ao acessar colunas pelo nome, usa-se Row
#         conn.row_factory = sqlite3.Row
#         return conn
#     #Log para o caso de erro
#     except sqlite3.Error as e:
#         print(f"❌ Erro ao conectar {e}")
#         return None


# #Selct no banco de dados para verificar se está tudo certo

# def select_tabelas():
#     conn = conectar_db()
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     print(cursor.fetchall())
#     conn.close()

# select_tabelas()


# def select_banco_de_dados() :
#     caminho_db = DB_PATH
#     print(f"Usando banco de dados: {caminho_db}")
#     print(f"Arquivo existe? {'Sim' if os.path.exists(caminho_db) else 'Não'}")
#     conn = conectar_db()
#     cursor = conn.cursor()
#     cursor.execute("""
#             SELECT name FROM sqlite_master WHERE type='table';
#                    """)
#     #Buscar todos os registros e printar
#     tabelas = cursor.fetchall()
    
#     if not tabelas:
#         print("❌ Nenhuma tabela encontrada no banco de dados.")
#     else:
#         for tabela in tabelas:
#             print(f"Tabela: {tabela['name']}")
#         print(f"✅ Verificação concluída! Total de tabelas: {len(tabelas)}")

#     conn.close()


# if __name__ == "__main__":
#     print("---🐛 Inicializando Banco de Dados ---")
#     conectar_db()
#     print(f"✅ Conectado com sucesso em {DB_PATH}!")
#     print("🔎 Verificando as tabelas da base civil de Rondônia: ")
#     select_banco_de_dados()
#     print("---🦋 Conexão com bando de dados concluída---")