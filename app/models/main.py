from thefuzz import fuzz
from unidecode import unidecode

def padroniza(texto):
    return unidecode(texto).strip().lower()
#Remover acentos e espaços aumenta o score de similaridade.

nome1 = "Letycia Vitórya De Jesus Filho"
nome2 = "Leticia Vitória Lima Firmino"

#Antes da padronização
print(f"Score Bruto: {fuzz.ratio(nome1, nome2)}")

#Após a padronização
print(f"Score padronizado: {fuzz.ratio(padroniza(nome1), padroniza(nome2))}")