import pandas as pd
import streamlit as st
import plotly.express as px
import json
import folium
from streamlit_folium import st_folium
#import datetime

# Configurações iniciais
st.set_page_config(layout='wide')
st.title("Vacinação Piauí 2024")

# URLs dos arquivos de dados
url_json = 'mun.geojson'
url_dataset = "https://raw.githubusercontent.com/mathe-u/datasets/refs/heads/main/vacinacao_piaui_ago_2024.csv"

# Funções para carregar dados com cache
@st.cache_data
def load_geo(url):
    with open(url, 'r') as file: 
        geo = json.load(file)
    return geo

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df['dt_vacina'] = pd.to_datetime(df['dt_vacina'])
    return df

#@st.cache_data
def load_map(dataframe, geojson_data):
    mapa_pi = folium.Map(location=[-7.2370, -42.5426], tiles='cartodbpositron', zoom_start=6)
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=dataframe,
        columns=['Código', 'Doses'],
        key_on='feature.properties.CD_MUN',
    ).add_to(mapa_pi)
    return mapa_pi

# Carregando os dados
municipios = load_geo(url_json)
df = load_data(url_dataset)

# Sidebar para filtros
st.sidebar.title("Filtros")
st.sidebar.subheader("Selecione uma data:")
date_i = st.sidebar.date_input('Início', value=df['dt_vacina'].min())
date_f = st.sidebar.date_input('Fim', value=df['dt_vacina'].max())
tipo_vacina = st.sidebar.selectbox(label='Selecione uma vacina', options=df['ds_vacina'].unique(), index=None)

# Filtrando o DataFrame pelas datas selecionadas
if date_i and date_f:
    df = df[(df['dt_vacina'] >= pd.to_datetime(date_i)) & (df['dt_vacina'] <= pd.to_datetime(date_f))]

# Filtrando o DataFrame pela vacina selecionada
if tipo_vacina:
    df = df[df['ds_vacina'] == tipo_vacina]

# Definindo faixas etárias
faixa_etaria = [0, 12, 18, 65, 120]
labels = ['0-12', '13-17', '18-64', '65+']

# Cálculos e agregações
faixa_paciente = pd.cut(df['nu_idade_paciente'], bins=faixa_etaria, labels=labels).value_counts().sort_values(ascending=True)
sexo_paciente = df['tp_sexo_paciente'].value_counts()
raca_cor_paciente = df['no_raca_cor_paciente'].value_counts(normalize=True).sort_values(ascending=True)
media_idade = df['nu_idade_paciente'].mean()
total_pacientes = df['co_paciente'].nunique()
nu_vacina_por_dia = df.groupby('dt_vacina').size().reset_index(name='Doses')

# Dados por município
municipio_vacinas = df['co_municipio_estabelecimento'].value_counts().reset_index()
municipio_vacinas.columns = ['Código', 'Doses']
municipio_vacinas['Código'] = municipio_vacinas['Código'].astype(str)

# Layout da página
col1, col2, col3, col4 = st.columns(4)
col5 = st.columns(1)[0]
col6, col7 = st.columns([3, 1])
col8, col9 = st.columns(2)

# Exibindo métricas
with col1:
    st.metric(label="TOTAL DE DOSES APLICADAS", value=f"{int(nu_vacina_por_dia['Doses'].sum())}")

with col2:
    st.metric(label="MÉDIA POR DIA", value=f"{nu_vacina_por_dia['Doses'].mean():.1f}")

with col3:
    st.metric(label="MÉDIA DE IDADE", value=f"{media_idade:.1f}")

with col4:
    st.metric(label="TOTAL DE PACIENTES", value=total_pacientes)

# Gráfico de linhas - Doses aplicadas por dia
with col5:
    fig = px.line(
        nu_vacina_por_dia,
        x='dt_vacina',
        y='Doses',
        title="Doses Aplicadas por Dia",
        labels={
            'dt_vacina': 'Data',
            'Doses': 'Quantidade de Doses'
        }
    )
    st.plotly_chart(fig, use_container_width=True)

# Gráfico de barras - Doses por município
with col6:
    st_folium(load_map(municipio_vacinas, url_json))
    #fig5 = px.bar(
    #    municipio_vacinas.sort_values('Doses', ascending=False).head(10),
    #    x='Código',
    #    y='Doses',
    #    title="Top 10 Municípios por Doses Aplicadas",
    #    labels={
    #        'Código': 'Código do Município',
    #        'Doses': 'Quantidade de Doses',
    #    }
    #)
    #st.plotly_chart(fig5, use_container_width=True)

# Gráfico de pizza - Distribuição por sexo
with col7:
    sexo_df = sexo_paciente.reset_index()
    sexo_df.columns = ['Sexo', 'Quantidade']
    fig_pie = px.pie(
        sexo_df,
        values='Quantidade',
        names='Sexo',
        title="Distribuição por Sexo",
        color_discrete_sequence=["#ff9999", "royalblue", "#aaaaaa"],
        hole=0.5,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Gráfico de barras horizontal - Proporção de raça/cor
with col8:
    raca_df = raca_cor_paciente.reset_index()
    raca_df.columns = ['Raça/Cor', 'Proporção']
    fig2 = px.bar(
        raca_df,
        x='Proporção',
        y='Raça/Cor',
        orientation='h',
        title='Proporção de Raça/Cor dos Vacinados',
    )
    st.plotly_chart(fig2, use_container_width=True)

# Gráfico de barras horizontal - Doses por faixa etária
with col9:
    faixa_df = faixa_paciente.reset_index()
    faixa_df.columns = ['Faixa Etária', 'Quantidade']
    fig4 = px.bar(
        faixa_df,
        x='Quantidade',
        y='Faixa Etária',
        orientation='h',
        title="Doses Aplicadas por Faixa Etária"
    )
    st.plotly_chart(fig4, use_container_width=True)
