# Pipeline de Dados Quantitativos: Impacto Macroeconômico no Setor Bancário (ITUB4)

Este projeto constrói um pipeline de dados ponta a ponta (End-to-End) para extrair, armazenar, modelar e analisar o impacto histórico da Taxa Selic sobre o preço de fechamento ajustado das ações do Itaú Unibanco (ITUB4).

## 🛠️ Arquitetura e Tecnologias
- **Linguagem:** Python 3.x
- **Ingestão de Dados:** APIs oficiais do Banco Central do Brasil (SGS) e Yahoo Finance (`yfinance`)
- **Armazenamento:** Banco de Dados Relacional Local (SQLite)
- **Transformação de Dados:** SQL Avançado (CTEs e Window Functions)
- **Análise & Gráficos:** Pandas, Seaborn e Matplotlib

## 📈 Status do Progresso
- [x] **Passo 1:** Ingestão automatizada de dados brutos e carga na camada de Staging do SQLite.
- [x] **Passo 2:** Modelagem de Dados com SQL (Alinhamento temporal e cálculo de lags).
- [x] **Passo 3:** Análise Estatística e Visualização de Dados (Python).
- [ ] **Passo 4:** Relatório de Insights Econômicos e Documentação Final.

## 📊 Visualizações Geradas

### Histórico de Ativos vs Macroeconomia
![Preço vs Juros](images/itub4_vs_selic.png)

### Matriz de Correlação Linear
![Matriz de Correlação](images/matriz_correlacao.png)

## 🚀 Como Executar
```bash
# 1. Ingestão
python scripts/ingestao_dados.py
# 2. Modelagem SQL
python scripts/modelagem_dados.py
# 3. Análise e Gráficos
python scripts/analise_graficos.py

## 🧠 Conclusões e Insights de Mercado

A análise quantitativa do pipeline gerou os seguintes insights sobre a relação entre o Itaú Unibanco (ITUB4) e a Taxa Selic:

1. **Resiliência do Spread Bancário:** Diferente de setores intensivos em capital e altamente alavancados (como Varejo e Construção Civil), o Itaú exibe resiliência em ciclos de juros altos. O retorno médio de 20 dias úteis manteve-se saudável mesmo em janelas de política monetária restritiva, capturando o ganho de spread e receitas de tesouraria.
2. **Eficiência de Arquitetura (SQL vs Python):** O alinhamento de granularidades temporais distintas (Ações = Diário, Selic = Mensal) foi resolvido inteiramente na camada de banco de dados (SQLite) através de junções por chaves de período (`ano_mes`). O cálculo de retorno móvel via Window Function (`LAG`) reduziu o custo de processamento em memória no Python, seguindo as melhores práticas de Analytics Engineering.