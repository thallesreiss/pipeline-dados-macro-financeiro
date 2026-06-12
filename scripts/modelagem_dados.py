import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "banco_macro.db"

def executar_modelagem_sql():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a modelagem dos dados com SQL Avançado...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Query SQL Avançada Corrigida (IS NOT NULL)
    query_transformacao = """
    CREATE TABLE fct_itub_selic_analytics AS
    WITH cte_itub_tratado AS (
        SELECT 
            strftime('%Y-%m', dt_referencia) AS ano_mes,
            dt_referencia,
            vl_fechamento_ajustado,
            LAG(vl_fechamento_ajustado, 20) OVER (ORDER BY dt_referencia) AS vl_fechamento_lag_20
        FROM stg_yfinance_itub
    ),
    cte_selic_tratada AS (
        SELECT 
            strftime('%Y-%m', dt_referencia) AS ano_mes,
            pct_selic_ano
        FROM stg_bcb_selic
    )
    SELECT 
        i.dt_referencia,
        i.ano_mes,
        i.vl_fechamento_ajustado,
        i.vl_fechamento_lag_20,
        ROUND(((i.vl_fechamento_ajustado - i.vl_fechamento_lag_20) / i.vl_fechamento_lag_20) * 100, 2) AS pct_retorno_20d,
        s.pct_selic_ano AS pct_selic_atual
    FROM cte_itub_tratado i
    LEFT JOIN cte_selic_tratada s ON i.ano_mes = s.ano_mes
    WHERE i.vl_fechamento_lag_20 IS NOT NULL;
    """
    
    # Garante uma execução limpa removendo a tabela antiga se existir
    cursor.execute("DROP TABLE IF EXISTS fct_itub_selic_analytics;")
    
    # Executa a query de transformação
    cursor.execute(query_transformacao)
    conn.commit()
    
    # Validação interna
    df_valida = pd.read_sql("SELECT COUNT(*) as total FROM fct_itub_selic_analytics", conn)
    total_linhas = df_valida['total'].values[0]
    
    conn.close()
    print(f"--> Sucesso! Tabela Fato 'fct_itub_selic_analytics' criada com {total_linhas} linhas prontas para análise.")

if __name__ == "__main__":
    try:
        executar_modelagem_sql()
    except Exception as e:
        print(f"\n[ERRO NA MODELAGEM]: {str(e)}")