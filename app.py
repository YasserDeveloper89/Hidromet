import streamlit as st import pandas as pd import numpy as np from io import BytesIO from docx import Document from fpdf import FPDF import plotly.graph_objects as go from datetime import datetime

Configurar la página

st.set_page_config(page_title="HydroClimaPRO", layout="wide")

Autenticación de usuarios simulada

USERS = { "admin": {"password": "admin123", "role": "Administrador"}, "analista": {"password": "analista123", "role": "Analista"}, "operador": {"password": "operador123", "role": "Operador"} }

Inicializar sesión

if 'logged_in' not in st.session_state: st.session_state.logged_in = False st.session_state.user = "" st.session_state.role = ""

def login(): st.title("🔐 Acceso a HydroClimaPRO") username = st.text_input("Usuario") password = st.text_input("Contraseña", type="password") if st.button("Iniciar sesión"): user = USERS.get(username) if user and user["password"] == password: st.session_state.logged_in = True st.session_state.user = username st.session_state.role = user["role"] st.experimental_rerun() else: st.error("Credenciales inválidas")

if not st.session_state.logged_in: login() st.stop()

Layout principal

st.sidebar.title("HydroClimaPRO - Menú") role = st.session_state.role st.sidebar.markdown(f"Usuario: {st.session_state.user}  ") st.sidebar.markdown(f"Rol: {role}")

menu = st.sidebar.radio("Navegación", ["Dashboard", "Cargar Datos", "Visualización", "Informe", "Configuración"])

if st.sidebar.button("Cerrar sesión"): st.session_state.logged_in = False st.session_state.user = "" st.session_state.role = "" st.experimental_rerun() st.stop()

Variables globales para datos cargados

df = pd.DataFrame()

if menu == "Dashboard": st.title("📊 Dashboard Corporativo - HydroClimaPRO") col1, col2, col3 = st.columns(3) col1.metric("Estaciones conectadas", "12", "+2") col2.metric("Informes generados", "37", "+5") col3.metric("Datos procesados", "145.000+", "+8.3%")

st.markdown("---")
st.subheader("Visión general de datos climatológicos")
fig = go.Figure()
fig.add_trace(go.Scatter(y=np.random.randn(30)*5+25, mode='lines+markers', name='Temp.'))
fig.add_trace(go.Scatter(y=np.random.rand(30)*50, mode='lines', name='Humedad'))
fig.update_layout(title='Tendencia mensual simulada', template='plotly_dark')
st.plotly_chart(fig, use_container_width=True)

elif menu == "Cargar Datos": st.title("📥 Cargar Datos Meteorológicos") uploaded_file = st.file_uploader("Carga tu archivo CSV", type=["csv"]) if uploaded_file: try: df = pd.read_csv(uploaded_file) st.session_state.df = df st.success("Datos cargados con éxito") st.dataframe(df.head()) except Exception as e: st.error(f"Error: {e}")

elif menu == "Visualización": st.title("📈 Visualización Interactiva") df = st.session_state.get("df", pd.DataFrame()) if not df.empty: columnas = df.select_dtypes(include=np.number).columns.tolist() columna = st.selectbox("Selecciona columna numérica", columnas) chart = go.Figure()

