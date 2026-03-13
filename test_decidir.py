import sys
sys.path.insert(0, 'C:/Users/leticia.lvlf/Desktop/Busca-fonetica/Busca-fonetica-nomes')

from app.models.busca_model import ler_csv, registrar_decisao_e_remover
import traceback

print("=== Testando ler_csv ===")
dados = ler_csv()
print(f"Registros encontrados: {len(dados)}")
if dados:
    print(f"Colunas: {list(dados[0].keys())}")
    print(f"Primeiro registro: {dados[0]}")

print("\n=== Testando registrar_decisao_e_remover ===")
try:
    registrar_decisao_e_remover('sim')
    print("OK - funcao executou sem erro")
except Exception as e:
    print("ERRO:")
    traceback.print_exc()
