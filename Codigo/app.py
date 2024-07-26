import streamlit as st
import pandas as pd
from sodapy import Socrata

st.title("Consulta de Datos de Contratación")

# Configuración de la API Socrata
client = Socrata("www.datos.gov.co", None)

# Solicitud de datos
@st.cache
def load_data():
    results = client.get("jbjy-vk9h", limit=1000)  # Reemplazar 'xxxx' con el endpoint específico
    return pd.DataFrame.from_records(results)

df = load_data()

# Mostrar datos
st.write(df)