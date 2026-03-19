import sqlite3
import requests
import base64
import os


USERNAME = 'linux'  
PASSWORD = 'ubuntuff2025'  

# Caminho para o banco de fotos local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOTOS_PATH = os.path.join(BASE_DIR, "..", "models", "fotos_extraidas.db")

def obter_token_api():
    """Realiza a autenticação na API e retorna o token de acesso."""
    encoded_credentials = base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode('utf-8')).decode('utf-8')
    auth_url = 'http://10.69.7.31/auth/login/'
    
    try:
        payload = {"uuid": "1D9D84D5-E18C-1407-4F77-8F29EF7F5A07", "mobile": False}
        headers = {'Authorization': f'Basic {encoded_credentials}'}
        
        response = requests.post(auth_url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json().get('token')
        return None
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return None

def buscar_foto_na_api_render(nome_completo, nome_pai, nome_mae):
    """
    Busca a foto baseada nos dados da Base Civil de RO.
    Retorna a string Base64 da imagem para exibição direta no HTML.
    """
    if not nome_completo or nome_completo == "NÃO INFORMADO":
        return None

    token = obter_token_api()
    if not token:
        return None

    headers = {'Authorization': f'Token {token}'}
    url_cards ='http://10.69.7.31/cards/humans/' 
    #filtrar pelo nome exato
    params = {'name': nome_completo.strip().upper()}
    
    try:
        response = requests.get(url_cards, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            resultados = response.json().get('results', [])
            if resultados:
                # Isso vai imprimir no seu terminal TODAS as chaves que o primeiro registro possui
                print(f"DEBUG - Chaves disponíveis no registro: {resultados[0].keys()}")
            
            for res in resultados:
                            # 1. Pegamos os campos específicos de filiação da API
                            # Verifique se o nome da chave na API é exatamente este (maiúsculas/minúsculas importam)
                            mae_api = res.get('Filiação 1 (mãe)', '').upper()
                            pai_api = res.get('Filiação 2 (pai)', '').upper()
                            
                            # 2. Comparamos com os dados que vieram da Base Civil de RO
                            # Usamos 'in' ou '==' dependendo de quão exata é a base da API
                            valida_mae = str(nome_mae).upper() in mae_api if nome_mae else True
                            valida_pai = str(nome_pai).upper() in pai_api if nome_pai else True

                            if valida_mae and valida_pai:
                                face_objects = res.get('face_objects', [])
                                if face_objects:
                                    foto_url = face_objects[0].get('thumbnail')
                                    
                                    if foto_url:
                                        img_resp = requests.get(foto_url, headers=headers, timeout=5)
                                        if img_resp.status_code == 200:
                                            return base64.b64encode(img_resp.content).decode('utf-8')
        
        return None
    except Exception as e:
        print(f"Erro ao buscar foto na API: {e}")
        return None

# --- Função de Suporte para salvar no Banco Local (após o 'Sim') ---
def salvar_foto_no_banco_local(id_api, nome, pai, mae, img_base64):
    """Salva a foto confirmada no SQLite para consultas futuras."""
    try:
        conn = sqlite3.connect(DB_FOTOS_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS galeria_fotos (
                id_api INTEGER PRIMARY KEY,
                nome TEXT, pai TEXT, mae TEXT,
                foto_binaria BLOB,
                data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Converte de volta de Base64 para Binário para salvar no DB
        img_binaria = base64.b64decode(img_base64)
        
        cursor.execute("""
            INSERT OR REPLACE INTO galeria_fotos (id_api, nome, pai, mae, foto_binaria)
            VALUES (?, ?, ?, ?, ?)
        """, (id_api, nome, pai, mae, img_binaria))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar no banco local: {e}")
        return False