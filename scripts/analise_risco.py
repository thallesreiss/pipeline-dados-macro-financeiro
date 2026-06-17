import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def calcular_drawdown(retornos):
    """Calcula a queda percentual do patrimônio em relação ao seu pico histórico máximo."""
    # 1. Simula o crescimento de R$ 1,00 ao longo do tempo
    patrimonio_acumulado = (1 + retornos).cumprod()
    
    # 2. Vai registrando qual foi o valor máximo que o patrimônio já atingiu até cada data
    picos_historicos = patrimonio_acumulado.cummax()
    
    # 3. Calcula o quanto o patrimônio atual caiu em relação a esse pico máximo
    drawdown = (patrimonio_acumulado - picos_historicos) / picos_historicos
    return drawdown

def analisar_risco_extremo():
    print("🛡️ Iniciando Motor de Análise de Risco (VaR e Max Drawdown)...")
    
    conn = sqlite3.connect('banco_macro.db')
    df_long = pd.read_sql("SELECT * FROM cotacoes_carteira", conn)
    conn.close()
    
    df_long['data'] = pd.to_datetime(df_long['data'])
    df_wide = df_long.pivot(index='data', columns='Ticker', values='Preco_Fechamento').dropna()
    
    retornos_diarios = df_wide.pct_change().dropna()
    
    # Inicializando um DataFrame para guardar as métricas de risco de cada ativo
    metricas_risco = pd.DataFrame(index=df_wide.columns)
    
    # Calculando o Value at Risk (VaR Histórico a 95% de confiança)
    # Significa: "Em 95% dos dias, a perda não será pior do que esse valor"
    metricas_risco['VaR_Diario_95%'] = retornos_diarios.quantile(0.05)
    
    # Calculando o Maximum Drawdown para cada ativo
    max_drawdowns = []
    for coluna in retornos_diarios.columns:
        dd = calcular_drawdown(retornos_diarios[coluna])
        max_drawdowns.append(dd.min()) # Pegamos o ponto mais fundo (mais negativo)
        
    metricas_risco['Max_Drawdown'] = max_drawdowns
    
    # Formatando para exibição percentual
    print("\n📊 TABELA DE RISCO EXTREMO (Piores Cenários):")
    tabela_formatada = metricas_risco.copy()
    tabela_formatada['VaR_Diario_95%'] = (tabela_formatada['VaR_Diario_95%'] * 100).map("{:.2f}%".format)
    tabela_formatada['Max_Drawdown'] = (tabela_formatada['Max_Drawdown'] * 100).map("{:.2f}%".format)
    
    # Ordenando do ativo mais arriscado (Maior queda) para o mais seguro
    tabela_formatada = tabela_formatada.sort_values('Max_Drawdown')
    print(tabela_formatada.to_string())
    
    # Visualização: O Drawdown do Índice da Bolsa (BOVA11) para termos como base de mercado
    ativo_benchmark = 'BOVA11'
    if ativo_benchmark in retornos_diarios.columns:
        dd_benchmark = calcular_drawdown(retornos_diarios[ativo_benchmark])
        
        plt.figure(figsize=(12, 5))
        plt.fill_between(dd_benchmark.index, dd_benchmark, 0, color='red', alpha=0.3)
        plt.plot(dd_benchmark.index, dd_benchmark, color='red', linewidth=1)
        
        plt.title(f'Sangria do Mercado: Maximum Drawdown do {ativo_benchmark} (Últimos 5 anos)', fontsize=14)
        plt.ylabel('Queda Percentual (%)')
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        
        os.makedirs('images', exist_ok=True)
        caminho_imagem = 'images/drawdown_mercado.png'
        plt.savefig(caminho_imagem, dpi=300)
        print(f"\n✅ Gráfico de risco salvo em: {caminho_imagem}")
        plt.show()

if __name__ == "__main__":
    analisar_risco_extremo()