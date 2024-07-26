import streamlit as st
import pandas as pd
from sodapy import Socrata

st.title("Consulta de Datos de Contratación")

# Configuración de la API Socrata
client = Socrata("www.datos.gov.co", None)

# Solicitud de datos
@st.cache
def load_data():
    consulta = """select * 
    where nombre_entidad = 'SUPERINTENDENCIA FINANCIERA DE COLOMBIA'"""
    results = client.get("jbjy-vk9h", query=consulta)
    results_df = pd.DataFrame.from_records(results)
    return results_df

df = load_data()

# Filtros de Búsqueda
st.sidebar.header('Filtros')
start_date = st.sidebar.date_input('Fecha de inicio', pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('Fecha de fin', pd.to_datetime('2021-01-01'))
df['fecha_de_firma'] = pd.to_datetime(df['fecha_de_firma']).dt.date
df_filtered = df[(df['fecha_de_firma'] >= start_date) & (df['fecha_de_firma'] <= end_date)]

# Visualización de Datos
st.write(df_filtered)

# Gráficos y Métricas
st.header('Métricas')
total_amount = df_filtered['monto'].sum()
total_contracts = len(df_filtered)
avg_amount = df_filtered['monto'].mean()
st.metric('Monto Total Contratado', f'${total_amount:,.2f}')
st.metric('Número Total de Contratos', total_contracts)
st.metric('Promedio del Monto por Contrato', f'${avg_amount:,.2f}')

st.header('Gráficos')
# Gráfico de Barras
bar_chart = alt.Chart(df_filtered).mark_bar().encode(
    x='tipo_contrato',
    y='count()',
    color='tipo_contrato'
)
st.altair_chart(bar_chart, use_container_width=True)

# Gráfico de Líneas
line_chart = alt.Chart(df_filtered).mark_line().encode(
    x='fecha',
    y='sum(monto)'
)
st.altair_chart(line_chart, use_container_width=True)

# Gráfico Circular (Pie Chart)
pie_chart = alt.Chart(df_filtered).mark_arc().encode(
    theta=alt.Theta(field='monto', type='quantitative'),
    color=alt.Color(field='tipo_contrato', type='nominal')
)
st.altair_chart(pie_chart, use_container_width=True)

