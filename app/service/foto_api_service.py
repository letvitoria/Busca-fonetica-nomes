import sqlite3
import requests
import base64
import os
import unicodedata
from urllib.parse import urljoin


USERNAME = 'linux'  
PASSWORD = 'ubuntuff2025'  

# Caminho para o banco de fotos local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOTOS_PATH = os.path.join(BASE_DIR, "..", "models", "fotos_extraidas.db")


def _obter_primeiro_campo(dado: dict, chaves_possiveis, default=''):
    for chave in chaves_possiveis:
        valor = dado.get(chave)
        if valor is not None and str(valor).strip() != '':
            return str(valor)
    return default


def _normalizar_texto(valor):
    if valor is None:
        return ''
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
    return ' '.join(texto.split())


def _extrair_face_objects(res):
    candidatos = [
        res.get('face_objects'),
        res.get('faces'),
        res.get('faceObject'),
        res.get('face_object'),
    ]
    for item in candidatos:
        if isinstance(item, list) and item:
            return item
    return []


def _extrair_url_foto(res):
    face_objects = _extrair_face_objects(res)

    if face_objects:
        foto_url = _obter_primeiro_campo(
            face_objects[0],
            ['thumbnail', 'thumb', 'url', 'image', 'image_url', 'photo', 'photo_url'],
            default=''
        )
        if foto_url:
            return foto_url

    return _obter_primeiro_campo(
        res,
        ['thumbnail', 'thumb', 'url', 'image', 'image_url', 'photo', 'photo_url', 'foto_url'],
        default=''
    )


def _baixar_imagem_base64(foto_url, headers, url_cards):
    if not foto_url:
        return None

    url_final = foto_url
    if foto_url.startswith('/'):
        url_final = urljoin(url_cards, foto_url)

    try:
        # Tenta com token (caso endpoint protegido)
        img_resp = requests.get(url_final, headers=headers, timeout=5)
        if img_resp.status_code == 200 and img_resp.content:
            return base64.b64encode(img_resp.content).decode('utf-8')

        # Fallback sem header (alguns endpoints de mídia são públicos)
        img_resp = requests.get(url_final, timeout=5)
        if img_resp.status_code == 200 and img_resp.content:
            return base64.b64encode(img_resp.content).decode('utf-8')
    except Exception as e:
        print(f"Erro ao baixar imagem em {url_final}: {e}")

    return None


def _buscar_foto_url_por_card(card_id, headers, url_base):
    """Consulta o endpoint de objetos de face para obter thumbnail da pessoa."""
    if not card_id:
        return ''

    try:
        url_faces = urljoin(url_base, 'objects/faces/')
        resp = requests.get(
            url_faces,
            headers=headers,
            params={'card': card_id, 'limit': 1},
            timeout=5,
        )
        if resp.status_code != 200:
            return ''

        resultados = resp.json().get('results', []) if isinstance(resp.json(), dict) else []
        if not resultados:
            return ''

        face = resultados[0]
        return _obter_primeiro_campo(
            face,
            ['thumbnail', 'thumb', 'url', 'image', 'image_url', 'source_photo'],
            default='',
        )
    except Exception as e:
        print(f"Erro ao buscar face por card {card_id}: {e}")
        return ''

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
    url_base = 'http://10.69.7.31/'
    url_cards = urljoin(url_base, 'cards/humans/')
    # Neste ambiente, "name_contains" retorna resultados consistentes para nome completo.
    params = {
        'name_contains': nome_completo.strip().upper(),
        'limit': 30,
    }
    
    try:
        response = requests.get(url_cards, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            resultados = response.json().get('results', [])
            if resultados:
                # Isso vai imprimir no seu terminal TODAS as chaves que o primeiro registro possui
                print(f"DEBUG - Chaves disponíveis no registro: {resultados[0].keys()}")
            
            nome_alvo = _normalizar_texto(nome_completo)
            nome_mae_norm = _normalizar_texto(nome_mae)
            nome_pai_norm = _normalizar_texto(nome_pai)
            fallback_img = None

            for res in resultados:
                nome_api = _normalizar_texto(
                    _obter_primeiro_campo(
                        res,
                        ['name', 'nome', 'nome_completo', 'full_name'],
                        default=''
                    )
                )

                # Evita pegar homônimo muito diferente quando a API retorna lista ampla.
                if nome_api and nome_alvo and (nome_alvo not in nome_api and nome_api not in nome_alvo):
                    continue

                meta = res.get('meta') if isinstance(res.get('meta'), dict) else {}

                # API pode variar o nome dos campos; tentamos múltiplas chaves.
                mae_api = _normalizar_texto(
                    _obter_primeiro_campo(
                        res,
                        ['Filiação 1 (mãe)', 'filiacao1', 'filiacao_1', 'mae', 'nome_mae'],
                        default=meta.get('mae', '')
                    )
                )
                pai_api = _normalizar_texto(
                    _obter_primeiro_campo(
                        res,
                        ['Filiação 2 (pai)', 'filiacao2', 'filiacao_2', 'pai', 'nome_pai'],
                        default=meta.get('pai', '')
                    )
                )

                # Se API não trouxer filiação, não bloqueia por esse critério.
                valida_mae = (nome_mae_norm in mae_api) if (nome_mae_norm and mae_api) else True
                valida_pai = (nome_pai_norm in pai_api) if (nome_pai_norm and pai_api) else True

                foto_url = _extrair_url_foto(res)
                if not foto_url:
                    foto_url = _buscar_foto_url_por_card(res.get('id'), headers, url_base)
                if not foto_url:
                    continue

                # Guarda uma opção de fallback para não voltar sem foto em cenários de campos inconsistentes.
                if fallback_img is None:
                    fallback_img = _baixar_imagem_base64(foto_url, headers, url_cards)

                if valida_mae and valida_pai:
                    img_base64 = _baixar_imagem_base64(foto_url, headers, url_cards)
                    if img_base64:
                        return img_base64

            if fallback_img:
                return fallback_img
        
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