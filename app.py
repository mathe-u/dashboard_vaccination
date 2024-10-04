import pandas as pd
import streamlit as st
import plotly.express as px
#import json
#import folium
#from streamlit_folium import st_folium
#import datetime


#url_json = 'mun.geojson'
url_dataset = "https://raw.githubusercontent.com/mathe-u/datasets/refs/heads/main/vacinacao_piaui_ago_2024.csv"

st.set_page_config(layout='wide')
st.title("Vacinação Piauí 2024")

#@st.cache_data
#def load_geo(url):
#    with open(url, 'r') as file: 
#        geo = json.load(file)
#        return geo

@st.cache_data
def load_data(url):
  df = pd.read_csv(url)
  df['dt_vacina'] = pd.to_datetime(df.dt_vacina)
  return df

#@st.cache_data
#def load_map():
#    mapa_pi = folium.Map(location=[-7.2370, -42.5426], tiles='cartodbpositron', zoom_start=6)
#    return mapa_pi

#municipios = json.load(open(url_json, 'r'))
df = load_data(url_dataset)

st.sidebar.title("Filtros")
st.sidebar.subheader("Selecione uma data:")
date_i = st.sidebar.date_input('Inicio', value=None)
date_f = st.sidebar.date_input('Fim', value=None)


if date_i is not None and date_f is not None:
    date_i = str(date_i)
    date_f = str(date_f)
    df = df[(df['dt_vacina'] >= date_i) & (df['dt_vacina'] <= date_f)]

faixa_etaria = [0, 12, 18, 65, 120]
labels = ['0-12', '13-17', '18-64', '65+']

#faixas = pd.cut(df['nu_idade_paciente'], bins=faixa_etaria, labels=labels)
faixa_paciente = pd.cut(df['nu_idade_paciente'], bins=faixa_etaria, labels=labels).value_counts().sort_values(ascending=True)

sexo_paciente = df["tp_sexo_paciente"].value_counts()
raca_cor_paciente = df["no_raca_cor_paciente"].value_counts(normalize=True).sort_values(ascending=True)
#municipio_paciente = df["no_municipio_paciente"].value_counts()
#vacina = df["ds_vacina"].value_counts().head(6)
#estabelecimento = df['no_fantasia_estalecimento'].value_counts()
media_idade = df['nu_idade_paciente'].mean()
#sexo_tempo2 = df.groupby('dt_vacina')['tp_sexo_paciente'].value_counts()
total_pacientes = df['co_paciente'].nunique()
#idade_paciente = df['nu_idade_paciente'].value_counts().head(6)
nu_vacina_por_dia = df.groupby('dt_vacina')['tp_sexo_paciente'].count()
#nu_vacina_por_dia.columns = ['Dia', 'Doses']

series2 = df['co_municipio_estabelecimento'].value_counts()
ds = pd.DataFrame(series2).reset_index()
ds.columns = ['cd', 'vac']
ds['cd'] = ds['cd'].astype(str)

col1, col2, col3, col4 = st.columns(4)
col5 = st.columns(1)[0]
col6, col7, = st.columns([3, 1])
col8, col9 = st.columns(2)

with col1:
    st.metric(label="TOTAL DE DOSES APLICADAS", value=f"{nu_vacina_por_dia.sum()}")

with col2:
    st.metric(label="MEDIA POR DIA", value=f"{nu_vacina_por_dia.mean():.1f}")

with col3:
    st.metric(label="MEDIA DE IDADE", value=f"{media_idade:.1f}")

with col4:
    st.metric(label="TOTAL DE PACIENTES", value=total_pacientes)

with col5:
    fig = px.line(
                  nu_vacina_por_dia,
                  y='tp_sexo_paciente',
                  title="Doses aplicadas por dia",
                  labels={
                      'tp_sexo_paciente': 'Doses',
                      'dt_vacina': 'Data'
                      }
              )
    st.plotly_chart(fig)

with col6:
    fig5 = px.bar(
                  ds,
                  x='cd',
                  y='vac',
                  title="Doses por municipio",
                  labels={
                      'cd': 'Codigo',
                      'vac': 'Doses',
                  }
              )
    st.plotly_chart(fig5)

with col7:
    fig_pie = px.pie(
                     sexo_paciente,
                     values='count',
                     names=sexo_paciente.index,
                     title="Sexo",
                     labels={"tp_sexo_paciente": "Sexo", "count": "Quantidade"},
                     color_discrete_sequence=["#ff9999", "royalblue", "#aaaaaa"],
                     hole=0.5,
                 )
    st.plotly_chart(fig_pie)

with col8:
    fig2 = px.bar(
                  raca_cor_paciente,
                  orientation='h',
                  labels={
                      'value': 'Proporção',
                      'no_raca_cor_paciente': 'Raça/Cor'
                  },
                  title='Proporção de raça/cor vacinados',
              )
    st.plotly_chart(fig2)

with col9:
    fig4 = px.bar(
                  faixa_paciente,
                  orientation='h',
                  labels={
                      'nu_idade_paciente': 'Faixa etária',
                      'value': 'Quantidade'
                  },
                  title="Doses aplicadas por faixa etária"
              )
    st.plotly_chart(fig4)

