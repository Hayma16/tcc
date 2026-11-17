# 🚗 Sistema de Análise de Telemetria Veicular

Sistema desenvolvido em Python para processamento e análise de dados de telemetria veicular, com visualização de métricas e indicadores de desempenho por meio de um dashboard interativo.

## 📌 Sobre o projeto

O objetivo é transformar dados brutos de telemetria em informações úteis para análise do comportamento e desempenho de um veículo.

O sistema utiliza um fluxo de processamento de dados (ETL) para realizar a leitura, transformação e análise de arquivos CSV.

## ⚙️ Funcionalidades

- Importação e leitura de dados em formato CSV.
- Processamento e transformação dos dados.
- Cálculo de velocidade média e RPM médio.
- Identificação de acelerações bruscas.
- Identificação de frenagens fortes.
- Análise do comportamento de condução.
- Cálculo de indicadores de desempenho (score).
- Visualização dos resultados em dashboard interativo.

## 🛠️ Tecnologias utilizadas

- **Python** — linguagem principal.
- **Pandas** — manipulação e análise de dados.
- **Streamlit** — desenvolvimento do dashboard.
- **CSV** — armazenamento e entrada dos dados.

## 📂 Estrutura do projeto

```text
tcc/
├── app.py
├── dados/
│   └── dados_ac.csv
├── requirements.txt
├── README.md
└── .gitignore
```

*Estrutura ilustrativa; será ajustada conforme a organização final dos arquivos.*

## 🚀 Como executar o projeto

### 1. Clone o repositório

```bash
git clone git@github.com:Hayma16/tcc.git
cd tcc
```

### 2. Crie um ambiente virtual

No Windows:

```powershell
py -m venv .venv
```

### 3. Ative o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instale as dependências

```bash
python -m pip install -r requirements.txt
```

### 5. Execute o dashboard

```bash
python -m streamlit run app.py
```

O Streamlit disponibilizará o dashboard no navegador.

## 📊 Indicadores analisados

| Indicador | Descrição |
|---|---|
| Velocidade média | Média de velocidade registrada |
| RPM médio | Média de rotações do motor |
| Aceleração brusca | Identificação de variações bruscas de velocidade |
| Frenagem forte | Identificação de desacelerações bruscas |
| Score de direção | Indicador de comportamento de condução |

## 🎯 Objetivo acadêmico

Projeto desenvolvido como trabalho de conclusão de curso, com foco na aplicação de conceitos de programação, análise de dados, processamento ETL e visualização de informações.

---

**Desenvolvido por:** [Hayma16](https://github.com/Hayma16)
