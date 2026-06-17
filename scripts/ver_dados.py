import sqlite3
import pandas as pd

def visualizar_banco():
    print("🔌 Conectando ao banco de dados SQLite...")
    conn = sqlite3.connect('banco_macro.db')
    
    # Usamos SQL puro para ler apenas as primeiras 10 linhas da tabela
    query = "SELECT * FROM cotacoes_carteira LIMIT 10"
    df = pd.read_sql(query, conn)
    
    print("\n📊 Primeiras linhas da tabela 'cotacoes_carteira':\n")
    print(df.to_string(index=False))
    
    # Contagem total para confirmar
    total = pd.read_sql("SELECT COUNT(*) as total FROM cotacoes_carteira", conn)
    print(f"\n✅ Total de registros confirmados no banco: {total['total'].iloc[0]}")
    
    conn.close()

if __name__ == "__main__":
    visualizar_banco()