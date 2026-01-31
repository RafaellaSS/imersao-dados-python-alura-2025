import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title='Dashboard de Salários na Área de Dados',
    page_icon='📊',
    layout='wide'
)

# --- Carregamento dos dados ---
df = pd.read_csv('https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv')

# Barra Lateral (filtros)
st.sidebar.header('Filtros:')

anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect('Ano', anos_disponiveis, default=anos_disponiveis)

senior_disponiveis = sorted(df['senioridade'].unique())
senior_selecionados = st.sidebar.multiselect('Senioridade', senior_disponiveis, default=senior_disponiveis)

contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect('Tipo de Contrato', contratos_disponiveis, default=contratos_disponiveis)

tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect('Tamanho da Empresa', tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtros = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senior_selecionados)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title('Dashboard de Análise de Salários na Área de Dados')
st.markdown('Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.')

# --- Métricas Principais (KPIs) ---
st.subheader('Métricas Gerais (Salário anual em USD)') #titulos das seções

if not df_filtros.empty :
    salario_medio = df_filtros['usd'].mean()
    salario_max = df_filtros['usd'].max()
    total_registros = df_filtros.shape[0]
    cargo_mais_frequente = df_filtros['cargo'].mode()[0]

else: #se a filtragem tiver vazia não tem registro pra calcular
    salario_medio, salario_max, total_registros, cargo_mais_frequente = 0, 0, 0, ''

col1, col2, col3, col4 = st.columns(4)
col1.metric('Salário Médio', f'${salario_medio:,.0f}')
col2.metric('Salário Máximo', f'${salario_max:,.0f}')
col3.metric('Total de Registros', f'${total_registros:,}')
col4.metric('Cargo mais Frequente', cargo_mais_frequente)

st.markdown('---')

# --- Análises Visuais com Plotly ---
st.subheader('📊 Gráficos')

col_graf1, col_graf2 = st.columns(2)  #2 graficos um do lado do outro

with col_graf1: # top 10 cargos com maior salário médio
    if not df_filtros.empty:                                  #10 valores maiores
        top_cargos = df_filtros.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(   #grafico de barras = px.bar
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',  #orientação horizontal, default é vertical
            title='Top 10 cargos por salário médio',
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )                           #mover o titulo p/ direita
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)  #comando para exibir o grafico com streamlit
    else:
        st.warning('Nenhum dado para exibir no gráfico de cargos.')

    with col_graf2:  #histograma distribuição dos salários
        if not df_filtros.empty:
            grafico_hist = px.histogram(
                df_filtros,
                x='usd',
                nbins=30,
                title='Distribuição de salários anuais',
                labels={'usd': 'Faixa Salarial (USD)', 'count': ''}
            )
            grafico_hist.update_layout(title_x=0.1)
            st.plotly_chart(grafico_hist, use_container_width=True)
        else:
            st.warning('Nenhum dado para exibir no gráfico de distribuição.')

col_graf3, col_graf4 = st.columns(2)
with col_graf3:
    if not df_filtros.empty:
        remoto_contagem = df_filtros['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(  #grafico pizza
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no gráfico dos tipos de trabalho.')

with col_graf4:  #DESAFIO - salario medio por país do cargo data scientist
    if not df_filtros.empty:
        df_ds = df_filtros[df_filtros['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_pais = px.choropleth(  #grafico de mapa
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
        )
        grafico_pais.update_layout(title_x=0.1)
        st.plotly_chart(grafico_pais, use_container_width=True)
    else: 
        st.warning('Nenhum dado para exibir no gráfico dos tipos de trabalho.')

# --- Tabela de Dados Detalhados ---
st.subheader('Dados Detalhados')
st.dataframe(df_filtros)

# streamlit run app.py no terminal pra rodar o dash