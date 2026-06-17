import sqlite3
import pandas as pd

DB_NAME = "banco_macro.db"

# Conecta ao banco
conn = sqlite3.connect(DB_NAME)

print("=== 1. LISTA DE TABELAS NO BANCO ===")
df_tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
print(df_tabelas)
print("\n" + "="*40 + "\n")

print("=== 2. PRIMEIRAS LINHAS DA TABELA FATO (fct_itub_selic_analytics) ===")
# Puxa apenas as 5 primeiras linhas para conferir as colunas
df_fato = pd.read_sql("SELECT * FROM fct_itub_selic_analytics LIMIT 5;", conn)
print(df_fato.to_string())

conn.close()