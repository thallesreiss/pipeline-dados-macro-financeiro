import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def analisar_correlacao_carteira():
    print("🔌 Extraindo dados da tabela 'cotacoes_carteira'...")
    conn = sqlite3.connect('banco_macro.db')
    
    # 1. Carregar os dados
    df_long = pd.read_sql("SELECT * FROM cotacoes_carteira", conn)
    conn.close()
    
    # Garantir que a coluna de data é reconhecida como tempo (datetime)
    df_long['data'] = pd.to_datetime(df_long['data'])
    
    # 2. Transformação: De Longo para Largo (Pivot)
    # Precisamos de uma matriz onde as colunas são os ativos e as linhas são os dias
    df_wide = df_long.pivot(index='data', columns='Ticker', values='Preco_Fechamento')
    
    # Limpar dias com dados nulos (ex: feriados onde SPYI11 negociou mas ITUB3 não)
    df_wide = df_wide.dropna()
    print(f"📈 Matriz alinhada: {df_wide.shape[0]} dias úteis cruzados para {df_wide.shape[1]} ativos.")
    
    # 3. Matemática Financeira: Retornos Diários
    # Markowitz não analisa preços brutos, analisa a variação percentual de um dia para o outro
    retornos_diarios = df_wide.pct_change().dropna()
    
    # 4. Cálculo da Matriz de Correlação (Pearson)
    matriz_correlacao = retornos_diarios.corr()
    
    # 5. Visualização (Heatmap)
    plt.figure(figsize=(14, 10))
    sns.heatmap(matriz_correlacao, annot=True, cmap='coolwarm', fmt=".2f", 
                linewidths=0.5, vmin=-1, vmax=1)
    
    plt.title('Matriz de Correlação de Retornos Diários (Últimos 5 Anos)', fontsize=16, pad=20)
    plt.tight_layout()
    
    # Garantir que a pasta images existe e salvar o gráfico
    os.makedirs('images', exist_ok=True)
    caminho_imagem = 'images/correlacao_carteira.png'
    plt.savefig(caminho_imagem, dpi=300)
    
    print(f"✅ Análise concluída! Mapa de calor salvo em: {caminho_imagem}")
    plt.show()

if __name__ == "__main__":
    analisar_correlacao_carteira()