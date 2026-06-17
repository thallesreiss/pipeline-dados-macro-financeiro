import streamlit as st
import sqlite3
import pandas as pd

# 1. Configuração da Página Web
st.set_page_config(page_title="Motor Quantitativo", layout="wide")
st.title("📊 Plataforma de Inteligência Quantitativa")
st.markdown("Bem-vindo ao motor de otimização de portfólios e análise de risco extremo.")

# 2. Conexão com o Banco de Dados (com cache para não travar o site)
@st.cache_data
def carregar_dados():
    conn = sqlite3.connect('banco_macro.db')
    df_long = pd.read_sql("SELECT * FROM cotacoes_carteira", conn)
    conn.close()
    
    df_long['data'] = pd.to_datetime(df_long['data'])
    return df_long.pivot(index='data', columns='Ticker', values='Preco_Fechamento').dropna()

df_wide = carregar_dados()

# 3. Barra Lateral (Inputs do Usuário)
st.sidebar.header("⚙️ Configurações da Carteira")
ativos_selecionados = st.sidebar.multiselect(
    "Selecione os ativos para análise:",
    options=df_wide.columns.tolist(),
    default=["ITUB3", "VALE3", "BBSE3", "BOVA11"]
)

# 4. Tela Principal (Visualização Dinâmica)
if ativos_selecionados:
    st.subheader("📈 Histórico de Preços Ajustados")
    # O Streamlit já cria um gráfico interativo automaticamente com os dados do Pandas!
    st.line_chart(df_wide[ativos_selecionados])
else:
    st.warning("👈 Por favor, selecione pelo menos um ativo na barra lateral.")