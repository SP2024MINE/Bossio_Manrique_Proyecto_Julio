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

# Mostrar datos
st.write(df)

