import pandas as pd
import streamlit as st
import plotly.express as px

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(page_title="Dashboard de Vendas", page_icon="🛒", layout="wide")

# ===============================
# CARREGAR OS DADOS
# ===============================
try:
    tabela = pd.read_excel("vendas.xlsx", parse_dates=["Data"])
except FileNotFoundError:
    st.error("❌ Arquivo 'vendas.xlsx' não encontrado! Coloque-o na mesma pasta do código.")
    st.stop()

# ===============================
# TÍTULO
# ===============================
st.title("📊 Dashboard de Vendas de Supermercado 🛒")
st.markdown("Análise interativa de vendas por **região**, **produto** e **data**.")

# ===============================
# FILTROS
# ===============================
st.sidebar.header("🔍 Filtros")

# Filtro de regiões
regioes = st.sidebar.multiselect("Região", sorted(tabela["Região"].unique()))

# Filtro de produtos
produtos = st.sidebar.multiselect("Produto", sorted(tabela["Produto"].unique()))

# Filtro por data
filtrar_por_data = st.sidebar.checkbox("Filtrar por Data", value=False)
if filtrar_por_data:
    data = st.sidebar.date_input("Data máxima", tabela["Data"].max().date())
    data = pd.Timestamp(data)
else:
    data = tabela["Data"].max()

# Filtrar por região antes do slider
dados_filtrados = tabela.copy()
if regioes:
    dados_filtrados = dados_filtrados[dados_filtrados["Região"].isin(regioes)]

# Slider dinâmico de valor de vendas
min_venda = float(dados_filtrados["Valor Venda"].min())
max_venda = float(dados_filtrados["Valor Venda"].max())

if min_venda == max_venda:
    max_venda += 1

valor_de_vendas = st.sidebar.slider(
    "Valor de Vendas",
    min_value=min_venda,
    max_value=max_venda,
    value=(min_venda, max_venda)
)

# ===============================
# APLICAR FILTROS
# ===============================
tabela_filtrada = dados_filtrados[
    (dados_filtrados["Valor Venda"] >= valor_de_vendas[0]) &
    (dados_filtrados["Valor Venda"] <= valor_de_vendas[1]) &
    (dados_filtrados["Data"] <= pd.to_datetime(data))
]

if produtos:
    tabela_filtrada = tabela_filtrada[tabela_filtrada["Produto"].isin(produtos)]

# ===============================
# KPIs (INDICADORES)
# ===============================
total_vendas = tabela_filtrada["Valor Venda"].sum()
ticket_medio = tabela_filtrada["Valor Venda"].mean() if len(tabela_filtrada) > 0 else 0
qtd_pedidos = len(tabela_filtrada)

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("💰 Total de Vendas", f"R$ {total_vendas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col_kpi2.metric("🛒 Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col_kpi3.metric("📦 Qtde. de Pedidos", f"{qtd_pedidos:,}".replace(",", "."))

# ===============================
# DEBUG DOS FILTROS
# ===============================
with st.expander("📌 Filtros aplicados"):
    st.write("Regiões:", regioes if regioes else "Todas")
    st.write("Produtos:", produtos if produtos else "Todos")
    st.write("Data máxima:", data.date() if hasattr(data, "date") else data)
    st.write("Intervalo de vendas:", valor_de_vendas)
    st.write("Linhas após filtro:", len(tabela_filtrada))

# ===============================
# GRÁFICOS
# ===============================
grafico_regiao = px.bar(
    tabela_filtrada, x="Região", y="Valor Venda",
    title="💰 Vendas por Região", text_auto=True,
    color="Região", color_discrete_sequence=px.colors.qualitative.Set2
)

grafico_produto = px.bar(
    tabela_filtrada, x="Produto", y="Valor Venda",
    title="📦 Vendas por Produto", text_auto=True,
    color="Produto", color_discrete_sequence=px.colors.qualitative.Pastel
)

grafico_data = px.line(
    tabela_filtrada.groupby("Data")["Valor Venda"].sum().reset_index(),
    x="Data", y="Valor Venda",
    title="📅 Evolução de Vendas ao Longo do Tempo",
    markers=True
)

# ===============================
# LAYOUT DOS GRÁFICOS
# ===============================
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(grafico_regiao, use_container_width=True)
with col2:
    st.plotly_chart(grafico_produto, use_container_width=True)

st.plotly_chart(grafico_data, use_container_width=True)

# ===============================
# RODAPÉ
# ===============================
st.markdown(
    """
    ---
    <div style="text-align: center; color: gray; font-size: 14px;">
        Desenvolvido por <b>Tatiana Kami</b> © 2025
    </div>
    """,
    unsafe_allow_html=True
)

