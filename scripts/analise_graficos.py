import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

DB_NAME = "banco_macro.db"
PASTA_OUTPUT = "images"

def gerar_analises_e_graficos():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a analise estatistica e geracao de graficos...")
    
    # Cria a pasta de imagens se ela nao existir (fundamental para o GitHub)
    if not os.path.exists(PASTA_OUTPUT):
        os.makedirs(PASTA_OUTPUT)
        
    conn = sqlite3.connect(DB_NAME)
    
    # Carrega a tabela fato completa para o Pandas
    query = "SELECT * FROM fct_itub_selic_analytics ORDER BY dt_referencia;"
    df = pd.read_sql(query, conn)
    df['dt_referencia'] = pd.to_datetime(df['dt_referencia'])
    
    conn.close()
    
    # =====================================================================
    # 1. ANALISE ESTATÍSTICA (TEXTO)
    # =====================================================================
    media_selic = df['pct_selic_atual'].mean()
    correlacao = df['pct_retorno_20d'].corr(df['pct_selic_atual'])
    
    print("\n" + "="*40)
    print(f"RESUMO DOS INSIGHTS QUANTITATIVOS:")
    print(f"--> Media historica da Selic no periodo: {media_selic:.2f}%")
    print(f"--> Correlacao de Pearson (Retorno 20d vs Selic): {correlacao:.4f}")
    
    # Comportamento em cenarios de juros
    retorno_juros_altos = df[df['pct_selic_atual'] > media_selic]['pct_retorno_20d'].mean()
    retorno_juros_baixos = df[df['pct_selic_atual'] <= media_selic]['pct_retorno_20d'].mean()
    
    print(f"--> Retorno medio de ITUB4 em janelas de Juros Altos: {retorno_juros_altos:.2f}%")
    print(f"--> Retorno medio de ITUB4 em janelas de Juros Baixos: {retorno_juros_baixos:.2f}%")
    print("="*40 + "\n")
    
    # =====================================================================
    # 2. VISUALIZAÇÃO 1: PREÇO DE ITUB4 VS SELIC AO LONGO DO TEMPO
    # =====================================================================
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    
    ax1 = sns.lineplot(data=df, x='dt_referencia', y='vl_fechamento_ajustado', color='orange', label='Preco ITUB4 (Eixo Esq.)', linewidth=2)
    ax1.set_ylabel('Preco Ajustado (R$)', color='orange', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='orange')
    
    # Criando o segundo eixo Y na mesma figura para a Selic
    ax2 = ax1.twinx()
    sns.lineplot(data=df, x='dt_referencia', y='pct_selic_atual', color='navy', label='Taxa Selic % (Eixo Dir.)', linewidth=2, ax=ax2)
    ax2.set_ylabel('Taxa Selic Anual (%)', color='navy', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='navy')
    
    plt.title('Itau Unibanco (ITUB4) vs Ciclo de Politica Monetaria (Selic)', fontsize=14, fontweight='bold', pad=15)
    ax1.get_legend().remove()
    
    # Salva o grafico na pasta de imagens do projeto
    caminho_grafico1 = os.path.join(PASTA_OUTPUT, 'itub4_vs_selic.png')
    plt.savefig(caminho_grafico1, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"--> Grafico 1 salvo com sucesso em: {caminho_grafico1}")
    
    # =====================================================================
    # 3. VISUALIZAÇÃO 2: MATRIZ DE CORRELAÇÃO
    # =====================================================================
    plt.figure(figsize=(6, 4))
    matrix = df[['vl_fechamento_ajustado', 'pct_retorno_20d', 'pct_selic_atual']].corr()
    
    sns.heatmap(matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, cbar=True)
    plt.title('Matriz de Correlacao Estatistica', fontsize=12, fontweight='bold', pad=10)
    
    caminho_grafico2 = os.path.join(PASTA_OUTPUT, 'matriz_correlacao.png')
    plt.savefig(caminho_grafico2, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"--> Grafico 2 salvo com sucesso em: {caminho_grafico2}")

if __name__ == "__main__":
    try:
        gerar_analises_e_graficos()
    except Exception as e:
        print(f"\n[ERRO NA ANALISE]: {str(e)}")