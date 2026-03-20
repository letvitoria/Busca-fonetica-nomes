# 🔍 Projeto de Busca Fonética e Validação de Identidade

Este sistema foi desenvolvido para automatizar e qualificar o processo de identificação de pessoas entre diferentes bases de dados (ex: Base Civil de Rondônia e BNMP). Através de algoritmos de processamento de linguagem natural e integração com APIs de imagem, o projeto permite que um agente humano valide identidades com alta precisão.

---

## 🚀 Funcionalidades Principais

### 1. Comparação Fonética Avançada

O sistema identifica registros onde o nome foi escrito de forma incorreta ou com variações regionais.

- **Processamento:** Utiliza TF-IDF e K-Nearest Neighbors (KNN) para encontrar candidatos.
- **Fuzzy Matching:** Aplica a biblioteca RapidFuzz para calcular um score de similaridade (0-100%) entre nomes e filiações.

---

### 2. Validação com Subsídio de Imagem (API FindFace)

Diferente de uma busca cega, o sistema traz a foto da Base Civil de RO em tempo real para o card de comparação.

- **Busca por Metadados:** A foto só é exibida se os campos de filiação (Filiação 1 e Filiação 2) na API coincidirem com os dados da base de Rondônia.
- **Decisão em Tempo Real:** O agente visualiza a foto antes de decidir, servindo como prova biométrica para confirmar o match.

---

## 🛠 Tecnologias

- **Backend:** Python / Flask (MVC)
- **Data Science:** Pandas, Scikit-learn, RapidFuzz
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados:** SQLite3 (para fotos extraídas) e CSV (para pendências)

---

## 🏁 Como Rodar o Projeto

1) **Abrir a pasta certa**: Abra no VS Code a pasta `Busca-fonetica\Busca-fonetica-nomes`.
3) **Ativar ambiente virtual**: No terminal, dentro dessa pasta, ative o `.venv` (no Windows PowerShell:
    `.\.venv\Scripts\Activate`) observando que ao ativar geralmente aparece `(.venv)` no início da linha.
5) **Instalar dependências (se for primeira vez)**:
   Caso exista um arquivo `requirements.txt`, execute a instalação; se não houver, instale manualmente as bibliotecas utilizadas no projeto, como Flask, pandas, requests, sklearn e rapidfuzz.
7)  **Garantir arquivo de pendências**:
   Verifique se o arquivo `app/models/pendentes_validacao_filiacao.csv` está presente, pois sem ele não haverá cards para validação.
9) **Iniciar o servidor**: Execute o arquivo principal `main.py`, que iniciará um servidor Flask local em modo debug.
6) **Abrir no navegador**: Acesse o endereço exibido no terminal (geralmente `http://127.0.0.1:5000/`), onde estarão disponíveis as telas principais de uso, como “Listar” (cards de validação) e “Relatório”.
