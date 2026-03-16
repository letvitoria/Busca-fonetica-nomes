import re
import unicodedata
import sqlite3
import os
import pandas as pd
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.neighbors import NearestNeighbors
from rapidfuzz import fuzz
from unidecode import unidecode
from tqdm import tqdm
import gc #Limpar a RAM


def normalizar_nome_para_comparacao(nome):
    """Normaliza apenas o nome para comparação de igualdade textual."""
    if nome is None:
        return ""

    texto = str(nome)
    if texto.lower() in ('none', 'null', 'nan'):
        return ""

    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(char for char in texto if not unicodedata.combining(char))
    texto = texto.upper().strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def executar_busca():
    #Ignorar no log avisos do sklearn 
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=UserWarning, module=r"sklearn\.utils\.parallel")


    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    PATH_RO = os.path.join(BASE_DIR, "models", "bases", "ro_civil.db")
    PATH_BNMP = os.path.join(BASE_DIR, "models", "bases", "bnmp.db")

    def normalizar_valor(valor):
        if pd.isna(valor):
            return None
        return valor

    def prefixar_campos(registro: dict, prefixo: str):
        return {
            f"{prefixo}{chave}": normalizar_valor(valor)
            for chave, valor in registro.items()
        }

    def localizar_coluna(df, candidatos, nome_base):
        mapa_lower = {col.lower(): col for col in df.columns}
        for candidato in candidatos:
            col = mapa_lower.get(candidato.lower())
            if col:
                return col
        raise ValueError(f"Coluna obrigatória não encontrada em {nome_base}: {candidatos}")

    def preparacao_fonetica(texto):
        if not texto or str(texto).lower() in ['NULL', 'None', '']: return ""
        texto = unidecode(str(texto)).upper().strip() #Remove acentuação
        substituicoes = {
            "PH": "F", "SH": "X", "CH": "X", "Y": "I", "K": "C", 
            "W": "V", "LL": "L", "SS": "S", "RR": "R", "Z": "S", 
            "GE": "JE", "GI": "JI", "TS": "S", "TZ": "S", "TH": "T"
        }
        for velho, novo in substituicoes.items():
            texto = texto.replace(velho, novo)
        return texto

    def montar_string_comparacao(nome, mae, pai):
        """Concatena os nomes disponíveis para criar uma identidade única."""
        partes = [str(nome)]
        if mae and str(mae).lower() not in ['NULL','none', '']: partes.append(str(mae))
        if pai and str(pai).lower() not in ['NULL','none', '']: partes.append(str(pai))
        return " ".join(partes)

    # --- CARREGAMENTO DOS DADOS ---
    print("--- Carregando Banco de Dados --- 🔎")
    conn_civilro = sqlite3.connect(PATH_RO)
    df_civil = pd.read_sql_query("SELECT DISTINCT * FROM pessoas", conn_civilro)
    conn_civilro.close()

    conn_bnmp = sqlite3.connect(PATH_BNMP)
    df_bnmp = pd.read_sql_query("SELECT DISTINCT * FROM dados_csv", conn_bnmp)
    conn_bnmp.close()

    col_id_civil = localizar_coluna(df_civil, ['nif', 'id', 'processo'], 'RO Civil')
    col_nome_civil = localizar_coluna(df_civil, ['nome', 'nome_completo'], 'RO Civil')
    col_mae_civil = localizar_coluna(df_civil, ['nome_mae', 'mae', 'filiacao1'], 'RO Civil')
    col_pai_civil = localizar_coluna(df_civil, ['nome_pai', 'pai', 'filiacao2'], 'RO Civil')

    col_id_bnmp = localizar_coluna(df_bnmp, ['id', 'id_bnmp'], 'BNMP')
    col_nome_bnmp = localizar_coluna(df_bnmp, ['Nome', 'nome', 'nome_completo'], 'BNMP')
    col_mae_bnmp = localizar_coluna(df_bnmp, ['Filiacao1', 'filiacao1', 'nome_mae', 'mae'], 'BNMP')
    col_pai_bnmp = localizar_coluna(df_bnmp, ['Filiacao2', 'filiacao2', 'nome_pai', 'pai'], 'BNMP')

    #Listas para acelerrar processamento
    nomes_civil = df_civil[col_nome_civil].tolist()
    maes_civil = df_civil[col_mae_civil].tolist()
    pais_civil = df_civil[col_pai_civil].tolist()
    ids_civil = df_civil[col_id_civil].tolist()

    nomes_bnmp = df_bnmp[col_nome_bnmp].tolist()
    maes_bnmp = df_bnmp[col_mae_bnmp].tolist()
    pais_bnmp = df_bnmp[col_pai_bnmp].tolist()
    ids_bnmp = df_bnmp[col_id_bnmp].tolist()

    #Preparação de Strings (nome pessoa + nome dos pais)
    print("--- Preparando dados para pesquisa...")
    civil_composto = [montar_string_comparacao(n, m, p) for n, m, p in zip(df_civil[col_nome_civil], df_civil[col_mae_civil], df_civil[col_pai_civil])]
    bnmp_composto = [montar_string_comparacao(n, m, p) for n, m, p in zip(df_bnmp[col_nome_bnmp], df_bnmp[col_mae_bnmp], df_bnmp[col_pai_bnmp])]

    # --- VETORIZAÇÃO  ---
    print("\n---- Padronizando as Strings para pesquisa ----")
    identidades_ref_fonetica = [preparacao_fonetica(s) for s in tqdm(civil_composto, desc="Limpando RO Civil")]
    identidades_alvo_fonetica = [preparacao_fonetica(s) for s in tqdm(bnmp_composto, desc="Limpando BNMP")]
    del civil_composto, bnmp_composto
    gc.collect()

    vetorizacao = TfidfVectorizer(analyzer='char', ngram_range=(2, 3), max_features=5000) #mudança teste
    tf_idf_matrix = vetorizacao.fit_transform(identidades_ref_fonetica)
    #Aprendiagem
    model = NearestNeighbors(n_neighbors=3, metric='cosine', n_jobs=-1)
    model.fit(tf_idf_matrix)
    tf_idf_bnmp = vetorizacao.transform(identidades_alvo_fonetica)


    #Inicia varredura (busca por nomes)
    print("\n---- Iniciando Varredura (Nome + Filiação) ----")

    print("\n---- Iniciando Varredura (Ignorando nomes idênticos/acentuados) ----")

    batch_size = 5000 
    resultados_para_humano = []
    pares_registrados = set()
    lote_vetores = None
    indices_lote = None

    with tqdm(total=len(ids_bnmp), desc="Processando: ") as pbar:
        for i in range(0, len(ids_bnmp), batch_size):
            fim = min(i + batch_size, len(ids_bnmp))
            lote_vetores = tf_idf_bnmp[i:fim]
            _, indices_lote = model.kneighbors(lote_vetores)
            
            for idx_lote, indices in enumerate(indices_lote):
                idx_global = i + idx_lote
                id_b = ids_bnmp[idx_global]
                
                # Normalização rigorosa para comparação de NOME: remove acentos e padroniza espaços
                n_b_limpo = normalizar_nome_para_comparacao(nomes_bnmp[idx_global])
                
                for vizinho_idx in indices:
                    id_c = ids_civil[vizinho_idx]
                    n_c_limpo = normalizar_nome_para_comparacao(nomes_civil[vizinho_idx])
                    
                    # Se os nomes forem iguais após normalização, ignora o par.
                    if n_b_limpo == n_c_limpo:
                        continue
                    
                    chave_par = (id_b, id_c)
                    if chave_par in pares_registrados:
                        continue
                    
                    score_composto = fuzz.token_sort_ratio(identidades_alvo_fonetica[idx_global], identidades_ref_fonetica[vizinho_idx])
                    
                    if score_composto >= 80:
                        dados_bnmp = prefixar_campos(df_bnmp.iloc[idx_global].to_dict(), 'bnmp_')
                        dados_ro_civil = prefixar_campos(df_civil.iloc[vizinho_idx].to_dict(), 'ro_civil_')

                        resultados_para_humano.append({
                            'id_bnmp': id_b,
                            'nome_bnmp': nomes_bnmp[idx_global],
                            'mae_bnmp': maes_bnmp[idx_global],
                            'pai_bnmp': pais_bnmp[idx_global],
                            'id_ro_civil': id_c,
                            'nome_ro_civil': nomes_civil[vizinho_idx],
                            'mae_ro_civil': maes_civil[vizinho_idx],
                            'pai_ro_civil': pais_civil[vizinho_idx],
                            'score_identidade': round(score_composto, 2),
                            **dados_bnmp,
                            **dados_ro_civil,
                        })
                        pares_registrados.add(chave_par)
            
            pbar.update(fim - i)

    # Liberar dataframes originais após o uso no laço de varredura
    del df_civil, df_bnmp
    gc.collect()

    # LIMPEZA ANTES DE SALVAR 
    del lote_vetores, indices_lote, identidades_ref_fonetica, identidades_alvo_fonetica
    gc.collect()

    # SALVAMENTO 
    output_path = os.path.join(BASE_DIR, 'models', 'pendentes_validacao_filiacao.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_final = pd.DataFrame(resultados_para_humano)
    if not df_final.empty:
        df_final = df_final.sort_values(by='score_identidade', ascending=False)
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n✅ Sucesso! {len(df_final)} candidatos encontrados.")
    else:
        print("\n❌ Nenhum candidato encontrado com as novas regras.")

    # Limpeza final
    del resultados_para_humano, pares_registrados, nomes_civil, maes_civil, pais_civil, ids_civil, nomes_bnmp, maes_bnmp, pais_bnmp, ids_bnmp
    del tf_idf_matrix, tf_idf_bnmp, model, vetorizacao

    gc.collect()
    print("RAM liberada!✅")
    return output_path


if __name__ == "__main__":
    executar_busca()