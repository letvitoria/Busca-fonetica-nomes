from thefuzz import fuzz
from unidecode import unidecode

def padroniza(texto):
    return unidecode(texto).strip().lower()
#Remover acentos e espaços aumenta o score de similaridade.

lista = {
    "Ana Carolina",
    "José da Silva",
    "Marcos Vinicius",
    "Beatriz Costa",
    "Amanda Nascimento",
    "João Paulo"
}

lista2 = {
    "Anna Karolina",
    "Jose da Silva",
    "Marcos Vinnicius",
    "Beatriz Da Costa",
    "Amanda Do Nascimento",
    "João Paulo Segundo"
}

for nome_2 in lista2:
    melhor_score = 0
    melhor_nome = ""
    for nome in lista:
        score = fuzz.ratio(padroniza(nome_2), padroniza(nome))
        if score > melhor_score:
            melhor_score = score
            melhor_nome = nome
        if melhor_score > 70:
            print(f'"{nome_2}" se parece mais com "{melhor_nome}" (Score: {melhor_score})\n')
        # else:
        #     print(f'"{nome_2}" -> "{melhor_nome}" Baixo Score: {melhor_score})\n') 