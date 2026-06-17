import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def otimizar_carteira():
    print("🧠 Iniciando o Motor de Otimização de Markowitz...")
    
    # 1. Carregar e alinhar os dados
    conn = sqlite3.connect('banco_macro.db')
    df_long = pd.read_sql("SELECT * FROM cotacoes_carteira", conn)
    conn.close()
    
    df_long['data'] = pd.to_datetime(df_long['data'])
    df_wide = df_long.pivot(index='data', columns='Ticker', values='Preco_Fechamento').dropna()
    
    # 2. Matemática Financeira: Retornos e Covariância Anualizados
    retornos_diarios = df_wide.pct_change().dropna()
    
    # Mercado financeiro brasileiro usa 252 dias úteis no ano
    retorno_esperado = retornos_diarios.mean() * 252
    matriz_covariancia = retornos_diarios.cov() * 252
    
    # 3. Simulação de Monte Carlo
    num_carteiras = 10000
    num_ativos = len(df_wide.columns)
    
    # Matriz para guardar: [0] Risco, [1] Retorno, [2] Índice Sharpe
    resultados = np.zeros((3, num_carteiras))
    pesos_registrados = []
    
    print(f"🎲 Simulando {num_carteiras} alocações diferentes de capital...")
    
    for i in range(num_carteiras):
        # Gerar pesos aleatórios que somem 100% (1.0)
        pesos = np.random.random(num_ativos)
        pesos /= np.sum(pesos)
        pesos_registrados.append(pesos)
        
        # Calcular Retorno e Risco (Volatilidade) da carteira simulada
        retorno_carteira = np.sum(pesos * retorno_esperado)
        risco_carteira = np.sqrt(np.dot(pesos.T, np.dot(matriz_covariancia, pesos)))
        
        # Índice Sharpe: Avalia o prêmio de risco (Retorno / Risco)
        sharpe_ratio = retorno_carteira / risco_carteira
        
        resultados[0,i] = risco_carteira
        resultados[1,i] = retorno_carteira
        resultados[2,i] = sharpe_ratio
        
    # 4. Descobrir a Carteira Vencedora
    indice_max_sharpe = np.argmax(resultados[2])
    melhores_pesos = pesos_registrados[indice_max_sharpe]
    
    print("\n🏆 CARTEIRA OTIMIZADA (Máximo Índice Sharpe):")
    for ativo, peso in zip(df_wide.columns, melhores_pesos):
        if peso > 0.01: # Mostrar apenas ativos que receberam mais de 1% de capital
            print(f"   {ativo}: {peso*100:.2f}%")
            
    print(f"\n📊 Expectativa de Retorno Anual: {resultados[1, indice_max_sharpe]*100:.2f}%")
    print(f"📉 Volatilidade Anual (Risco): {resultados[0, indice_max_sharpe]*100:.2f}%")
    
    # 5. Visualização: A Fronteira Eficiente
    plt.figure(figsize=(12, 8))
    plt.scatter(resultados[0,:], resultados[1,:], c=resultados[2,:], cmap='viridis', marker='o', s=10, alpha=0.3)
    plt.colorbar(label='Índice Sharpe (Qualidade da Carteira)')
    
    # Destacar a carteira campeã com uma estrela vermelha
    plt.scatter(resultados[0, indice_max_sharpe], resultados[1, indice_max_sharpe], marker='*', color='r', s=500, label='Carteira Ideal')
    
    plt.title('Fronteira Eficiente de Markowitz (Simulação de Monte Carlo)', fontsize=15, pad=15)
    plt.xlabel('Risco (Volatilidade Anual)', fontsize=12)
    plt.ylabel('Retorno Esperado Anual', fontsize=12)
    plt.legend()
    
    os.makedirs('images', exist_ok=True)
    caminho_imagem = 'images/fronteira_eficiente.png'
    plt.savefig(caminho_imagem, dpi=300)
    print(f"\n✅ Gráfico da Fronteira Eficiente salvo em: {caminho_imagem}")
    plt.show()

if __name__ == "__main__":
    otimizar_carteira()