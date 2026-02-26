# Depois: Remover os 'prints'
def executar_busca():
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

    #Ignorar no log avisos do sklearn
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=UserWarning, module=r"sklearn\.utils\.parallel")


    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    PATH_RO = os.path.join(BASE_DIR, "models", "bases", "ro_civil.db")
    PATH_BNMP = os.path.join(BASE_DIR, "models", "bases", "bnmp.db")

    def preparacao_fonetica(texto):
        if not texto or str(texto).lower() in ['nan', 'None', '']: return ""
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
        if mae and str(mae).lower() not in ['nan', 'none', '']: partes.append(str(mae))
        if pai and str(pai).lower() not in ['nan', 'none', '']: partes.append(str(pai))
        return " ".join(partes)

    # --- CARREGAMENTO DOS DADOS ---
    print("--- Carregando Banco de Dados --- 🔎")
    conn_civilro = sqlite3.connect(PATH_RO)
    df_civil = pd.read_sql_query("SELECT DISTINCT nif, nome, nome_mae, nome_pai FROM pessoas", conn_civilro)
    conn_civilro.close()

    conn_bnmp = sqlite3.connect(PATH_BNMP)
    df_bnmp = pd.read_sql_query("SELECT DISTINCT id, Nome, Filiacao1, Filiacao2 FROM dados_csv", conn_bnmp) 
    conn_bnmp.close()

    #Listas para acelerrar processamento
    nomes_civil = df_civil['nome'].tolist()
    maes_civil = df_civil['nome_mae'].tolist()
    pais_civil = df_civil['nome_pai'].tolist()
    ids_civil = df_civil['nif'].tolist()

    nomes_bnmp = df_bnmp['Nome'].tolist()
    maes_bnmp = df_bnmp['Filiacao1'].tolist()
    pais_bnmp = df_bnmp['Filiacao2'].tolist()
    ids_bnmp = df_bnmp['id'].tolist()

    #Preparação de Strings (nome pessoa + nome dos pais)
    print("--- Preparando dados para pesquisa...")
    civil_composto = [montar_string_comparacao(n, m, p) for n, m, p in zip(df_civil['nome'], df_civil['nome_mae'], df_civil['nome_pai'])]
    bnmp_composto = [montar_string_comparacao(n, m, p) for n, m, p in zip(df_bnmp['Nome'], df_bnmp['Filiacao1'], df_bnmp['Filiacao2'])]

    # --- VETORIZAÇÃO  ---
    print("\n---- Padronizando as Strings para pesquisa ----")
    identidades_ref_fonetica = [preparacao_fonetica(s) for s in tqdm(civil_composto, desc="Limpando RO Civil")]
    identidades_alvo_fonetica = [preparacao_fonetica(s) for s in tqdm(bnmp_composto, desc="Limpando BNMP")]

    # Liberar dataframes originais 
    del df_civil, df_bnmp, civil_composto, bnmp_composto
    gc.collect()

    vetorizacao = TfidfVectorizer(analyzer='char', ngram_range=(2, 3), max_features=5000) #mudança teste
    tf_idf_matrix = vetorizacao.fit_transform(identidades_ref_fonetica)
    #Aprendiagem
    model = NearestNeighbors(n_neighbors=3, metric='cosine', n_jobs=-1)
    model.fit(tf_idf_matrix)
    tf_idf_bnmp = vetorizacao.transform(identidades_alvo_fonetica)


    #Inicia varredura (busca por nomes)
    print("\n---- Iniciando Varredura (Nome + Filiação) ----")

    batch_size = 5000 
    resultados_para_humano = []
    pares_registrados = set()

    print("\n---- Iniciando Varredura (Ignorando nomes idênticos/acentuados) ----")

    batch_size = 5000 
    resultados_para_humano = []
    pares_registrados = set()

    with tqdm(total=len(ids_bnmp), desc="Processando: ") as pbar:
        for i in range(0, len(ids_bnmp), batch_size):
            fim = min(i + batch_size, len(ids_bnmp))
            lote_vetores = tf_idf_bnmp[i:fim]
            distancias_lote, indices_lote = model.kneighbors(lote_vetores)
            
            for idx_lote, indices in enumerate(indices_lote):
                idx_global = i + idx_lote
                id_b = ids_bnmp[idx_global]
                
                # Normalização rigorosa para comparação: remove acentos e espaços extras
                n_b_limpo = unidecode(str(nomes_bnmp[idx_global])).strip().upper()
                
                for vizinho_idx in indices:
                    id_c = ids_civil[vizinho_idx]
                    n_c_limpo = unidecode(str(nomes_civil[vizinho_idx])).strip().upper()
                    
                    # --- CORREÇÃO: Compara nomes SEM acentuação ---
                    # Se após remover os acentos forem iguais, o script ignora.
                    if n_b_limpo == n_c_limpo:
                        continue
                    
                    chave_par = (id_b, id_c)
                    if chave_par in pares_registrados:
                        continue
                    
                    score_composto = fuzz.token_sort_ratio(identidades_alvo_fonetica[idx_global], identidades_ref_fonetica[vizinho_idx])
                    
                    if score_composto >= 80:
                        resultados_para_humano.append({
                            'id_bnmp': id_b,
                            'nome_bnmp': nomes_bnmp[idx_global],
                            'mae_bnmp': maes_bnmp[idx_global],
                            'pai_bnmp': pais_bnmp[idx_global],
                            'id_ro_civil': id_c,
                            'nome_ro_civil': nomes_civil[vizinho_idx],
                            'mae_ro_civil': maes_civil[vizinho_idx],
                            'pai_ro_civil': pais_civil[vizinho_idx],
                            'score_identidade': round(score_composto, 2)
                        })
                        pares_registrados.add(chave_par)
            
            pbar.update(fim - i)

    # LIMPEZA ANTES DE SALVAR 
    del lote_vetores, distancias_lote, indices_lote, identidades_ref_fonetica, identidades_alvo_fonetica
    gc.collect()

    # SALVAMENTO 
    df_final = pd.DataFrame(resultados_para_humano)
    if not df_final.empty:
        df_final = df_final.sort_values(by='score_identidade', ascending=False)
        output_path = os.path.join(BASE_DIR, 'pendentes_validacao_filiacao.csv')
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n✅ Sucesso! {len(df_final)} candidatos encontrados.")
    else:
        print("\n❌ Nenhum candidato encontrado com as novas regras.")

    # Limpeza final
    del resultados_para_humano, pares_registrados, nomes_civil, maes_civil, pais_civil, ids_civil, nomes_bnmp, maes_bnmp, pais_bnmp, ids_bnmp
    del tf_idf_matrix, tf_idf_bnmp, model, vetorizacao

    gc.collect()
    print("✅ RAM liberada com sucesso.")
    return output_path 