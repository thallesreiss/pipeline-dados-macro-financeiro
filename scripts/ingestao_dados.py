import sqlite3
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime

# =====================================================================
# CONSTANTES E CONFIGURAÇÕES
# =====================================================================
DB_NAME = "banco_macro.db"
DATA_INICIO = "01/01/2019"  # Padrão BCB (DD/MM/AAAA)
DATA_FIM = datetime.now().strftime("%d/%m/%Y")

# Código da Selic acumulada no mês anualizada (SGS - Banco Central)
CODIGO_SELIC = 4189  

# Ticker do Itaú Unibanco na B3
TICKER_ATIVO = "ITUB4.SA"  

# =====================================================================
# 1. EXTRAÇÃO: API DO BANCO CENTRAL (SGS)
# =====================================================================
def extrair_selic(codigo_serie, data_inicio, data_fim):
    """Busca os dados de uma série temporal no SGS do Banco Central."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Coletando dados da Selic na API do BCB...")
    
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}"
    response = requests.get(url)
    
    if response.status_code == 200:
        dados_json = response.json()
        df = pd.DataFrame(dados_json)
        
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = pd.to_numeric(df['valor'])
        
        df.rename(columns={'data': 'dt_referencia', 'valor': 'pct_selic_ano'}, inplace=True)
        return df
    else:
        raise Exception(f"Erro ao acessar API do BCB. Status: {response.status_code}")

# =====================================================================
# 2. EXTRAÇÃO: API YAHOO FINANCE (VERSÃO BLINDADA)
# =====================================================================
def extrair_dados_ativo(ticker, data_inicio, data_fim):
    """Busca o histórico de cotações de um ativo via yfinance tratando variações de colunas."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Coletando dados de {ticker} no Yahoo Finance...")
    
    dt_ini_yf = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
    dt_fim_yf = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
    
    # Forçamos o download trazendo apenas o preço de Fechamento Ajustado para simplificar a estrutura
    df_yf = yf.download(ticker, start=dt_ini_yf, end=dt_fim_yf, progress=False)
    
    if df_yf.empty:
        raise Exception(f"Nenhum dado retornado para o ticker {ticker}.")
    
    # Se o Pandas trouxer colunas MultiIndex (com níveis), nós "achatamos" para o primeiro nível
    if isinstance(df_yf.columns, pd.MultiIndex):
        df_yf.columns = df_yf.columns.get_level_values(0)
        
    df_yf.reset_index(inplace=True)
    
    # Renomeia a coluna de data independentemente de como ela venha (Date ou data)
    df_yf.rename(columns={df_yf.columns[0]: 'dt_referencia'}, inplace=True)
    
    # Mecanismo de busca inteligente para a coluna de fechamento ajustado ou fechamento comum
    coluna_fechamento = None
    for col in df_yf.columns:
        if 'adj' in col.lower() and 'close' in col.lower():
            coluna_fechamento = col
            break
            
    # Se não achar o "Adj Close", busca o "Close" padrão
    if not coluna_fechamento:
        for col in df_yf.columns:
            if 'close' in col.lower():
                coluna_fechamento = col
                break

    if not coluna_fechamento:
        raise Exception(f"Não foi possível encontrar a coluna de preço. Colunas disponíveis: {list(df_yf.columns)}")
    
    # Filtra apenas o necessário
    df_limpo = df_yf[['dt_referencia', coluna_fechamento]].copy()
    df_limpo.columns = ['dt_referencia', 'vl_fechamento_ajustado']
    
    # Remove fuso horário para o SQLite aceitar sem problemas
    df_limpo['dt_referencia'] = pd.to_datetime(df_limpo['dt_referencia']).dt.tz_localize(None)
    
    # Remove linhas onde o preço seja nulo (feriados ou dias sem negociação)
    df_limpo.dropna(subset=['vl_fechamento_ajustado'], inplace=True)
    
    return df_limpo

# =====================================================================
# 3. CARGA: SALVANDO NO BANCO SQLITE
# =====================================================================
def salvar_no_banco(df, nome_tabela, db_name=DB_NAME):
    """Cria uma conexão com o SQLite e salva os dados brutos."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Salvando dados na tabela '{nome_tabela}'...")
    
    conn = sqlite3.connect(db_name)
    df.to_sql(nome_tabela, conn, if_exists='replace', index=False)
    conn.close()
    print(f"--> Sucesso! Tabela '{nome_tabela}' populada com {len(df)} registros.")

# =====================================================================
# EXECUÇÃO PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    try:
        df_selic = extrair_selic(CODIGO_SELIC, DATA_INICIO, DATA_FIM)
        df_ativo = extrair_dados_ativo(TICKER_ATIVO, DATA_INICIO, DATA_FIM)
        
        salvar_no_banco(df_selic, "stg_bcb_selic")
        salvar_no_banco(df_ativo, "stg_yfinance_itub")
        
        print(f"\n[FIM DO PASSO 1] O banco '{DB_NAME}' foi criado com sucesso na raiz do projeto!")
        
    except Exception as e:
        print(f"\n[ERRO NA OPERAÇÃO]: {str(e)}")