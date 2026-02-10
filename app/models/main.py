import sqlite3
import os
import pandas as pd
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from rapidfuzz import fuzz
from unidecode import unidecode
from tqdm import tqdm

# Silencia avisos de paralelização do sklearn
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    module=r"sklearn\.utils\.parallel",
)

# Configurações de Caminho
DIR = os.path.dirname(os.path.abspath(__file__))
PATH_RO = os.path.join(DIR, "bases", "ro_civil.db")
PATH_BNMP = os.path.join(DIR, "bases", "bnmp.db")

# --- FUNÇÃO DE NORMALIZAÇÃO FONÉTICA (PT-BR) ---
def preparacao_fonetica(texto):
    if not texto:
        return ""
    # 1. Remove acentos e coloca em caixa alta
    texto = unidecode(str(texto)).upper().strip()
    
    # 2. Substituições fonéticas manuais (Simulando Metaphone para nomes BR)
    substituicoes = {
        "PH": "F", "SH": "X", "CH": "X", 
        "Y": "I", "K": "C", "W": "V",
        "LL": "L", "SS": "S", "RR": "R",
        "Z": "S", "GE": "JE", "GI": "JI",
        "TS": "S", "TZ": "S", "TH": "T"
    }
    for velho, novo in substituicoes.items():
        texto = texto.replace(velho, novo)
    
    return texto

# --- CARREGAMENTO DOS DADOS ---
print("--- Carregando Bancos de Dados --- 🔎")

conn_civilro = sqlite3.connect(PATH_RO)
df_civil = pd.read_sql_query("SELECT rowid, nome FROM pessoas", conn_civilro)
conn_civilro.close()

conn_bnmp = sqlite3.connect(PATH_BNMP)
df_bnmp = pd.read_sql_query("SELECT id, Nome FROM dados_csv", conn_bnmp) 
conn_bnmp.close()

# Convertendo colunas para listas (Acesso MUITO mais rápido que .iloc no loop)
nomes_civil_originais = df_civil['nome'].tolist()
ids_civil = df_civil['rowid'].tolist()
nomes_bnmp_originais = df_bnmp['Nome'].tolist()
ids_bnmp = df_bnmp['id'].tolist()

print(f"Bases carregadas: RO Civil ({len(nomes_civil_originais)}) | BNMP ({len(nomes_bnmp_originais)})")

# --- VETORIZAÇÃO ---
print("\n---- Iniciando Pré-processamento Fonético e Vetorização ----")
# Criamos a versão "limpa" para o algoritmo trabalhar
nomes_ref_fonetico = [preparacao_fonetica(n) for n in tqdm(nomes_civil_originais, desc="Limpando RO Civil")]
nomes_alvo_fonetico = [preparacao_fonetica(n) for n in tqdm(nomes_bnmp_originais, desc="Limpando BNMP")]

# analyzer='char' e ngram_range=(2, 4) capturam sub-partes dos nomes
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
tf_idf_matrix = vectorizer.fit_transform(nomes_ref_fonetico)

# --- TREINAMENTO DO MODELO ---
# n_neighbors=5 busca os 5 nomes mais parecidos foneticamente
model = NearestNeighbors(n_neighbors=5, metric='cosine', n_jobs=-1)
model.fit(tf_idf_matrix)

# Vetoriza a base BNMP para busca
tf_idf_bnmp = vectorizer.transform(nomes_alvo_fonetico)

# --- BUSCA INTELIGENTE COM PROGRESSO REAL ---
print("\n---- Iniciando Varredura Vetorial ----")

batch_size = 10000  # Processamos de 10 em 10 mil para atualizar o log
total_nomes = tf_idf_bnmp.shape[0]
resultados_para_humano = []

# Barra de progresso para a busca matemática
with tqdm(total=total_nomes, desc="Buscando Similaridades: ") as pbar:
    for i in range(0, total_nomes, batch_size):
        # Seleciona o lote atual
        fim = min(i + batch_size, total_nomes)
        lote_vetores = tf_idf_bnmp[i:fim]
        
        # Realiza a busca apenas para este lote
        distancias_lote, indices_lote = model.kneighbors(lote_vetores)
        
        # Processa os resultados do lote atual para o RapidFuzz
        for idx_lote, (distancias, indices) in enumerate(zip(distancias_lote, indices_lote)):
            idx_global = i + idx_lote
            nome_alvo_limpo = nomes_alvo_fonetico[idx_global]
            
            for vizinho_idx in indices:
                # Validação final com RapidFuzz
                score_final = fuzz.token_sort_ratio(nome_alvo_limpo, nomes_ref_fonetico[vizinho_idx])
                
                if score_final >= 80:
                    resultados_para_humano.append({
                        'id_bnmp': ids_bnmp[idx_global],
                        'nome_bnmp': nomes_bnmp_originais[idx_global],
                        'id_ro_civil': ids_civil[vizinho_idx],
                        'nome_ro_civil': nomes_civil_originais[vizinho_idx],
                        'score_fonetico': round(score_final, 2)
                    })
        
        pbar.update(fim - i) #

# --- SALVAMENTO ---
print("\n--- Finalizando e salvando resultados ---")
df_final = pd.DataFrame(resultados_para_humano)

# Salva em arquivo CSV os resultados com score mais alto
if not df_final.empty:
    df_final = df_final.sort_values(by='score_fonetico', ascending=False)
    output_path = os.path.join(DIR, 'pendentes_validacao_fonetica.csv')
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Sucesso! {len(df_final)} possíveis matches encontrados em: {output_path}")
else:
    print("Nenhum match encontrado com os critérios atuais.")