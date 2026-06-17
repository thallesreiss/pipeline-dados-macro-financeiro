import yfinance as yf
import pandas as pd
import sqlite3

def extrair_dados_ativos():
    # 1. Definir a sua carteira alvo
    tickers_base = [
        "ITUB3", "RECV3", "BBSE3", "VLID3", "POMO3", "SPYI11", 
        "ISAE4", "BRBI11", "VALE3", "KEPL3", "PLPL3", "CPFE3",
        "BOVA11", "SMAL11", "IVVB11", "IRFM11"
    ]
    
    # O Yahoo Finance exige '.SA' para ativos brasileiros
    tickers_yf = [f"{t}.SA" for t in tickers_base]
    
    print(f"📥 Baixando dados históricos para {len(tickers_base)} ativos...")
    
    # 2. Extração: Baixando os últimos 5 anos
    df_bruto = yf.download(tickers_yf, period="5y")
    
    # Lidando com a matriz do yfinance: pegamos apenas a coluna 'Close'
    df_fechamento = df_bruto['Close']
    
    # 3. Transformação: De Largo para Longo (Tidy Data)
    df_long = df_fechamento.reset_index().melt(id_vars=['Date'], var_name='Ticker', value_name='Preco_Fechamento')
    
    # Limpeza de nulos (finais de semana ou dias sem negociação)
    df_long = df_long.dropna()
    df_long.rename(columns={'Date': 'data'}, inplace=True)
    
    # Removendo o '.SA' para o banco de dados ficar limpo e padronizado
    df_long['Ticker'] = df_long['Ticker'].str.replace('.SA', '', regex=False)
    
    print(f"🔄 Dados transformados! Total de registros: {len(df_long)}")
    
    # 4. Carga: Conectar ao SQLite e persistir
    conn = sqlite3.connect('banco_macro.db')
    
    # Salvando em uma nova tabela específica para esta carteira
    df_long.to_sql('cotacoes_carteira', conn, if_exists='replace', index=False)
    
    conn.close()
    print("✅ Dados salvos com sucesso na tabela 'cotacoes_carteira' do SQLite!")

if __name__ == "__main__":
    extrair_dados_ativos()