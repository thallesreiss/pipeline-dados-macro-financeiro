import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def realizar_backtest():
    print("⏱️ Iniciando o Motor de Backtesting Histórico...")
    
    # 1. Conexão e estruturação dos dados
    conn = sqlite3.connect('banco_macro.db')
    df_long = pd.read_sql("SELECT * FROM cotacoes_carteira", conn)
    conn.close()
    
    df_long['data'] = pd.to_datetime(df_long['data'])
    df_wide = df_long.pivot(index='data', columns='Ticker', values='Preco_Fechamento').dropna()
    
    retornos = df_wide.pct_change().dropna()
    
    # 2. Recalculando rapidamente a Carteira Ideal (Máximo Sharpe)
    print("🔍 Encontrando os pesos da Carteira Ideal para o período...")
    retorno_esp = retornos.mean() * 252
    cov_mat = retornos.cov() * 252
    
    num_simulacoes = 5000
    num_ativos = len(df_wide.columns)
    melhor_sharpe = -1
    pesos_ideais = np.zeros(num_ativos)
    
    for _ in range(num_simulacoes):
        p = np.random.random(num_ativos)
        p /= np.sum(p)
        ret = np.sum(p * retorno_esp)
        risco = np.sqrt(np.dot(p.T, np.dot(cov_mat, p)))
        sharpe = ret / risco
        if sharpe > melhor_sharpe:
            melhor_sharpe = sharpe
            pesos_ideais = p
    print("\n🏆 PESOS DA CARTEIRA IDEAL (Backtest):")
    for ativo, peso in zip(df_wide.columns, pesos_ideais):
        if peso > 0.01:  # Mostra apenas os ativos que receberam mais de 1%
            print(f"   {ativo}: {peso*100:.2f}%")
    print("\n")

    # 3. Construindo a linha do tempo
    # Multiplicamos o retorno de cada ativo pelo seu peso definido pelo algoritmo
    retorno_diario_carteira = (retornos * pesos_ideais).sum(axis=1)
    
    # 4. Simulando o crescimento de R$ 100,00
    patrimonio_carteira = 100 * (1 + retorno_diario_carteira).cumprod()
    
    if 'BOVA11' in retornos.columns:
        patrimonio_bova = 100 * (1 + retornos['BOVA11']).cumprod()
    else:
        print("⚠️ BOVA11 não encontrado na base para atuar como benchmark.")
        return

    # 5. Visualização Comparativa
    print("🏁 Gerando gráfico da corrida...")
    plt.figure(figsize=(12, 6))
    
    # Desenhando as linhas (Verde para a nossa carteira, Vermelho tracejado para o mercado)
    plt.plot(patrimonio_carteira.index, patrimonio_carteira, label='Carteira Otimizada (Markowitz)', color='#2ca02c', linewidth=2)
    plt.plot(patrimonio_bova.index, patrimonio_bova, label='Benchmark (BOVA11)', color='#d62728', linewidth=1.5, linestyle='--')
    
    plt.title('Backtest: Carteira Otimizada vs Mercado (Crescimento de R$ 100)', fontsize=15, pad=15)
    plt.ylabel('Evolução do Patrimônio (R$)', fontsize=12)
    plt.xlabel('Data', fontsize=12)
    plt.legend()
    plt.grid(alpha=0.3)
    
    os.makedirs('images', exist_ok=True)
    caminho_imagem = 'images/backtest_comparativo.png'
    plt.savefig(caminho_imagem, dpi=300)
    print(f"✅ Gráfico de Backtest salvo em: {caminho_imagem}")
    
    # 6. O Veredito Financeiro
    rent_carteira = (patrimonio_carteira.iloc[-1] / 100 - 1) * 100
    rent_bova = (patrimonio_bova.iloc[-1] / 100 - 1) * 100
    print(f"\n💰 RENTABILIDADE ACUMULADA (Últimos 5 Anos):")
    print(f"   Carteira IA: +{rent_carteira:.2f}%")
    print(f"   BOVA11:      +{rent_bova:.2f}%")
    
    plt.show()

if __name__ == "__main__":
    realizar_backtest()