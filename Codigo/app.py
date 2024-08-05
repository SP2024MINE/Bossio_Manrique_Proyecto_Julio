import streamlit as st
import pandas as pd
from sodapy import Socrata
import altair as alt

st.title("Consulta de Datos de Contratación")

# Configuración de la API Socrata
client = Socrata("www.datos.gov.co", None)

# Solicitud de datos
@st.cache_data
def load_data():
    consulta = """select * 
    where nombre_entidad = 'SUPERINTENDENCIA FINANCIERA DE COLOMBIA'"""
    results = client.get("jbjy-vk9h", query=consulta)
    results_df = pd.DataFrame.from_records(results)
    return results_df

df = load_data()

# Filtros de Búsqueda
st.sidebar.header('Filtros')

#Filtro Fecha
df['fecha_de_firma'] = pd.to_datetime(df['fecha_de_firma']).dt.date
start_date = st.sidebar.date_input('Fecha de inicio', pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('Fecha de fin', pd.to_datetime('2021-01-01'))

#Filtro tipo de contrato
tipo_contrato = ['Todos'] + list(df['tipo_de_contrato'].unique())
s_tipo_contrato = st.sidebar.selectbox('Tipo de contrato', tipo_contrato)

#Filtro por contratista
contratista = ['Todos'] + list(df['proveedor_adjudicado'].unique())
s_contratista = st.sidebar.selectbox('Proveedor adjudicado',contratista)

# Aplicar filtros
df_filtered = df[(df['fecha_de_firma'] >= start_date) & (df['fecha_de_firma'] <= end_date)]

if s_tipo_contrato != 'Todos':
    df_filtered = df_filtered[df_filtered['tipo_de_contrato'] == s_tipo_contrato]

if s_contratista != 'Todos':
    df_filtered = df_filtered[df_filtered['proveedor_adjudicado'] == s_contratista]

# Visualización de Datos
st.write(df_filtered)

# Gráficos y Métricas
st.header('Métricas')
df_filtered['valor_del_contrato'] = pd.to_numeric(df_filtered['valor_del_contrato'], errors='coerce')
total_amount = df_filtered['valor_del_contrato'].sum()
total_contracts = len(df_filtered)
avg_amount = df_filtered['valor_del_contrato'].mean()
st.metric('Monto Total Contratado', f'${total_amount:,.2f}')
st.metric('Número Total de Contratos', total_contracts)
st.metric('Promedio del Monto por Contrato', f'${avg_amount:,.2f}')

st.header('Gráficos')
# Gráfico de Barras
df_filtered['tipo__de_contrato'] = df_filtered['tipo_de_contrato'].astype(str)
bar_chart = alt.Chart(df_filtered).mark_bar().encode(
    x='tipo_de_contrato',
    y='count()',
    color='tipo_de_contrato'
)
st.altair_chart(bar_chart, use_container_width=True)

# Gráfico de Líneas
line_chart = alt.Chart(df_filtered).mark_line().encode(
    x='fecha_de_firma',
    y='sum(valor_del_contrato)'
)
st.altair_chart(line_chart, use_container_width=True)

# Gráfico Circular (Pie Chart)
pie_chart = alt.Chart(df_filtered).mark_arc().encode(
    theta=alt.Theta(field='valor_del_contrato', type='quantitative'),
    color=alt.Color(field='tipo_de_contrato', type='nominal')
)
st.altair_chart(pie_chart, use_container_width=True)

# Análisis de Contratistas
st.header('Análisis de Contratistas')
        
# Agrupar por contratista
contractor_summary = df_filtered.groupby('proveedor_adjudicado').agg(num_contracts=pd.NamedAgg(column='valor_del_contrato', aggfunc='size'),
total_amount=pd.NamedAgg(column='valor_del_contrato', aggfunc='sum')).reset_index()

# número de contratos y monto total
contractor_summary = contractor_summary.sort_values(by=['num_contracts', 'total_amount'], ascending=False)

# tabla con el resumen
st.write(contractor_summary)

# Gráfico de Contratistas
bar_chart_contractor = alt.Chart(contractor_summary).mark_bar().encode(x=alt.X('contratista:O', title='Contratista'), 
                                                                       y=alt.Y('num_contracts:Q', title='Número de Contratos'),
                                                                       color='total_amount:Q',
                                                                       tooltip=['contratista:N', 'num_contracts:Q', 'total_amount:Q']).properties(title='Número de Contratos por Contratista')
st.altair_chart(bar_chart_contractor, use_container_width=True)

# Gráfico de Monto Total Contratado por Contratista
bar_chart_amount = alt.Chart(contractor_summary).mark_bar().encode(x=alt.X('contratista:O', title='Contratista'), y=alt.Y('total_amount:Q', title='Monto Total Contratado'),color='total_amount:Q',tooltip=['contratista:N', 'total_amount:Q']).properties(title='Monto Total Contratado por Contratista')
st.altair_chart(bar_chart_amount, use_container_width=True)