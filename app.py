# app.py
import pandas as pd
import streamlit as st
import altair as alt
import datetime

st.set_page_config(layout="wide")

def clean_value(value):
    """Limpa a coluna 'value' removendo símbolos de moeda e vírgulas."""
    if isinstance(value, str):
        # Remove " z" e as vírgulas, depois converte para float
        return float(value.replace(' z', '').replace(',', ''))
    return float(value)

def process_uploaded_file(uploaded_file, file_date):
    """Processa um arquivo CSV enviado pelo usuário."""
    df = pd.read_csv(uploaded_file)
    df['date'] = pd.to_datetime(file_date)
    
    if 'value' in df.columns:
        df['value'] = df['value'].apply(clean_value)
    
    # Remove colunas que podem não ser comuns para evitar erros na concatenação
    if 'bonus' in df.columns:
        df = df.drop(columns=['bonus'])
        
    return df

st.title('Análise de Preços de Itens com Upload de Arquivos')

# --- Barra Lateral para Upload e Filtros ---
st.sidebar.header('1. Faça o Upload dos Dados')

# Datas padrão baseadas nos nomes dos arquivos originais
date_vendors = datetime.date(2025, 8, 23)
date_sellers = datetime.date(2025, 7, 24)

uploaded_vendors_file = st.sidebar.file_uploader("Arquivo de Vendedores (Vendors)", type=['csv'])
vendors_date = st.sidebar.date_input("Data do arquivo de Vendedores", date_vendors)

uploaded_sellers_file = st.sidebar.file_uploader("Arquivo de Compradores (Sellers)", type=['csv'])
sellers_date = st.sidebar.date_input("Data do arquivo de Compradores", date_sellers)

# --- Corpo Principal da Aplicação ---
if uploaded_vendors_file is not None and uploaded_sellers_file is not None:
    # Processa os arquivos enviados
    vendors_df = process_uploaded_file(uploaded_vendors_file, vendors_date)
    sellers_df = process_uploaded_file(uploaded_sellers_file, sellers_date)

    # Combina os dois DataFrames
    df = pd.concat([vendors_df, sellers_df], ignore_index=True)

    st.sidebar.header('2. Filtros de Análise')
    item_list = sorted(df['item'].unique())
    selected_item = st.sidebar.selectbox('Selecione um item para analisar:', options=item_list)

    # Filtra os dados para o item selecionado
    item_df = df[df['item'] == selected_item].copy()
    item_df['date_str'] = item_df['date'].dt.strftime('%Y-%m-%d')

    st.header(f'Análise de Preço para: {selected_item}')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Distribuição de Preços por Data')
        box_plot = alt.Chart(item_df).mark_boxplot().encode(
            x=alt.X('date_str:N', title='Data'),
            y=alt.Y('value:Q', title='Preço')
        ).properties(
            title=f'Distribuição de Preços'
        )
        st.altair_chart(box_plot, use_container_width=True)

    with col2:
        st.subheader('Estatísticas Resumidas')
        st.write(item_df.groupby('date')['value'].describe().T)

    st.subheader('Dados Detalhados')
    st.dataframe(item_df[['date', 'vendor', 'store name', 'amount', 'value']])
else:
    st.info('Por favor, faça o upload dos dois arquivos CSV na barra lateral para iniciar a análise.')
