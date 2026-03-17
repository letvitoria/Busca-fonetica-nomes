import csv
import os
import pandas as pd
from typing import Optional, Tuple


def _valor_exibicao(valor):
    if valor is None:
        return 'NÃO INFORMADO'

    texto = str(valor).strip()
    if not texto or texto.lower() in ('nan', 'none', 'null'):
        return 'NÃO INFORMADO'

    return valor


def montar_campos_exibicao(pessoa: dict):
    """Monta campos completos para exibição na tela, por base, com fallback legado."""
    pessoa = pessoa or {}

    campos_bnmp = {}
    campos_ro_civil = {}

    for chave, valor in pessoa.items():
        if chave.startswith('bnmp_'):
            campos_bnmp[chave[len('bnmp_'):]] = _valor_exibicao(valor)
        elif chave.startswith('ro_civil_'):
            campos_ro_civil[chave[len('ro_civil_'):]] = _valor_exibicao(valor)

    # Compatibilidade com arquivo antigo (sem prefixos de base)
    if not campos_bnmp:
        mapa_legado_bnmp = {
            'id_bnmp': 'id',
            'nome_bnmp': 'nome',
            'mae_bnmp': 'nome_mae',
            'pai_bnmp': 'nome_pai',
            'bnmp_campo': 'bnmp',
        }
        for chave_legada, nome_saida in mapa_legado_bnmp.items():
            if chave_legada in pessoa:
                campos_bnmp[nome_saida] = _valor_exibicao(pessoa.get(chave_legada))

    if not campos_ro_civil:
        mapa_legado_civil = {
            'id_ro_civil': 'processo',
            'nome_ro_civil': 'nome',
            'mae_ro_civil': 'nome_mae',
            'pai_ro_civil': 'nome_pai',
            'cpf_ro_civil': 'cpf',
            'rg_ro_civil': 'rg',
        }
        for chave_legada, nome_saida in mapa_legado_civil.items():
            if chave_legada in pessoa:
                campos_ro_civil[nome_saida] = _valor_exibicao(pessoa.get(chave_legada))

    nome_bnmp = campos_bnmp.get('Nome') or campos_bnmp.get('nome') or _valor_exibicao(pessoa.get('nome_bnmp'))
    nome_ro_civil = campos_ro_civil.get('nome') or campos_ro_civil.get('Nome') or _valor_exibicao(pessoa.get('nome_ro_civil'))

    return {
        'campos_bnmp': campos_bnmp,
        'campos_ro_civil': campos_ro_civil,
        'nome_bnmp': nome_bnmp,
        'nome_ro_civil': nome_ro_civil,
    }

def ler_csv():
    # Caminho dinâmico para encontrar o arquivo na mesma pasta do model
    caminho = os.path.join(os.path.dirname(__file__), 'pendentes_validacao_filiacao.csv')
    
    if os.path.exists(caminho):
        # Lemos o CSV e convertemos para uma lista de dicionários
        df = pd.read_csv(caminho)
        return df.to_dict(orient='records')
    return []


def obter_primeiro_e_total_pendencias() -> Tuple[Optional[dict], int]:
    """Lê apenas o necessário para a tela: primeiro registro e total pendente."""
    caminho = os.path.join(os.path.dirname(__file__), 'pendentes_validacao_filiacao.csv')

    if not os.path.exists(caminho):
        return None, 0

    with open(caminho, mode='r', encoding='utf-8-sig', newline='') as arquivo:
        leitor = csv.DictReader(arquivo)
        primeiro = next(leitor, None)
        if primeiro is None:
            return None, 0

        total = 1 + sum(1 for _ in leitor)
        return primeiro, total

def registrar_decisao_e_remover(decisao: str):
    print(f"DEBUG: Decisão recebida no Model: '{decisao}'")
    caminho = os.path.join(os.path.dirname(__file__), 'pendentes_validacao_filiacao.csv')
    caminho_decididos = os.path.join(os.path.dirname(__file__), 'decididos.csv')

    if not os.path.exists(caminho):
        return False

    # 1. LER TUDO PARA A MEMÓRIA E FECHAR O ARQUIVO IMEDIATAMENTE
    linhas_restantes = []
    primeiro = None
    colunas_pendentes = []

    with open(caminho, mode='r', encoding='utf-8-sig', newline='') as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas_pendentes = leitor.fieldnames or []
        lista_completa = list(leitor)
        if lista_completa:
            primeiro = lista_completa[0]
            linhas_restantes = lista_completa[1:]

    if primeiro is None:
        return False

    # 2. SALVAR O DECIDIDO
    colunas_decididos = list(colunas_pendentes)
    if 'decisao' not in colunas_decididos:
        colunas_decididos.append('decisao')

    escrever_cabecalho = not os.path.exists(caminho_decididos) or os.path.getsize(caminho_decididos) == 0
    with open(caminho_decididos, mode='a', encoding='utf-8-sig', newline='') as arquivo_decididos:
        escritor = csv.DictWriter(arquivo_decididos, fieldnames=colunas_decididos)
        if escrever_cabecalho:
            escritor.writeheader()
        linha_decidida = dict(primeiro)
        linha_decidida['decisao'] = decisao
        escritor.writerow(linha_decidida)

    # 3. REESCREVER O PENDENTES (SEM O PRIMEIRO)
    with open(caminho, mode='w', encoding='utf-8-sig', newline='') as arquivo_pendentes:
        escritor = csv.DictWriter(arquivo_pendentes, fieldnames=colunas_pendentes)
        escritor.writeheader()
        escritor.writerows(linhas_restantes)

    return True

