import sqlite3
from thefuzz import fuzz
from unidecode import unidecode
import logging
import pandas as pd


def padroniza(texto):
    return unidecode(str(texto)).strip().lower() if texto else ""
#Definição de caminhos baseada na estrutura de pastas

# 1. Conectar aos dois bancos de dados
print("--Conectando com banco de dados")
conn1 = sqlite3.connect('Busca-fonetica-nomes/app/models/bases/bnmp.db')
conn2 = sqlite3.connect('Busca-fonetica-nomes/app/models/bases/ro_civil.db')
print("Conexão criada com sucesso! ✅")

# 2. Extrair os nomes para listas
cursor1 = conn1.cursor()
cursor1.execute("SELECT Nome FROM dados_csv")
#Usamos set() para eliminar duplicadas e acelerar a busca
#Duplicadas de nomes exatamente iguais
nomes_banco_1 = {linha[0] for linha in cursor1.fetchall() if linha[0]}
cursor2 = conn2.cursor()
print("--- Exibindo os nomes encontrados em BNMP: ---")
#print(nomes_banco_1) Feito a verificação, está retornando o dado correto
cursor2.execute("SELECT nome FROM pessoas")
nomes_banco_2 = {linha[0] for linha in cursor2.fetchall() if linha[0]}
print(f"\n{'='*80}")
# print(nomes_banco_2) Feito a verificação, está retornando o dado correto
conn1.close()
conn2.close()

#Lógica de comparação
resultados = []
print("-- Loop de resultados iniciado...")


for nome_externo in nomes_banco_2:
    nome_2_limpo = padroniza(nome_externo)
    melhor_score = 0
    melhor_nome_correspondente = ""

    for nome_interno in nomes_banco_1:
        score = fuzz.ratio(nome_2_limpo, padroniza(nome_interno))
        
        if score > melhor_score:
            melhor_score = score
            melhor_nome_correspondente = nome_interno
        
        # Se achou uma similaridade perfeita, não precisa testar o resto para este nome
        if melhor_score == 100:
            break

#Verificação de score acima de 70 (chance alta de ser a mesma pessoa)
    if melhor_score > 90:
        resultados.append({
            "original": nome_externo,
            "correspondente": melhor_nome_correspondente,
            "score": melhor_score
        })
print("Aguardando fim do loop...")


#Mostrar resultados no log
print(f"\n{'='*80}")
print(f"RESULTADOS - Nomes com similaridade acima de 90%")
print(f"\n{'='*80}")

for resultado in resultados:
    print(f'"{resultado ["original"]}" se parece com "{resultado["correspondente"]}" (score: {resultado["score"]})')

print(f"Total de correspondencias encontradas: {len(resultados)}")
print(f"\n{'='*80}")
print("Verifica")
