import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

# --- Configuración de página ---
st.set_page_config(page_title="HydroClima PRO", layout="wide")

# --- Usuarios ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tec456", "role": "tecnico"},
    "observador": {"password": "obs789", "role": "observador"}
}

# --- Estado de sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.data_loaded = False
    st.session_state.df = pd.DataFrame()

# --- Función de Login ---
def login():
    st.title("🔐 Iniciar Sesión - HydroClima PRO")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.success(f"Bienvenido, {username.upper()} ({st.session_state.role.upper()})")
        else:
            st.error("Credenciales incorrectas")

# --- Exportar Word ---
def export_word(df):
    doc = Document()
    doc.add_heading('Informe de Datos Hidrometeorológicos', 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, item in enumerate(row):
            row_cells[i].text = str(item)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    st.download_button(label="📥 Descargar Word", data=buffer, file_name="informe.docx")

# --- Exportar PDF ---
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align='C')
    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.cell(200, 10, txt=row, ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    st.download_button("📥 Descargar PDF", buffer, file_name="informe.pdf")

# --- Visualización Pro ---
def visualizacion_pro(df):
    st.subheader("📊 Visualización Interactiva")
    selected_col = st.selectbox("Selecciona columna para graficar:", df.columns)
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df[selected_col], mode='lines+markers', line=dict(color='cyan')))
    fig.update_layout(template='plotly_dark', title=f"Gráfico de {selected_col}", height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- Panel de Admin ---
def admin_panel():
    st.title("📋 Panel de Administrador")
    st.info("Control total del sistema. Acceso a todos los módulos.")

    uploaded_file = st.file_uploader("Cargar archivo CSV", type="csv")
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.data_loaded = True

    if st.session_state.data_loaded:
        df = st.session_state.df
        st.dataframe(df)
        export_pdf(df)
        export_word(df)
        visualizacion_pro(df)

        st.subheader("📡 Conexión a dispositivos")
        if st.button("Simular conexión a estación meteorológica"):
            st.success("📶 Conexión establecida con el dispositivo de medición")

# --- Panel Técnico ---
def tecnico_panel():
    st.title("🔧 Panel Técnico")
    uploaded_file = st.file_uploader("Cargar archivo CSV", type="csv")
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.data_loaded = True

    if st.session_state.data_loaded:
        df = st.session_state.df
        st.dataframe(df)
        export_word(df)
        visualizacion_pro(df)

# --- Panel Observador ---
def observador_panel():
    st.title("👁️ Panel Observador")
    if st.session_state.data_loaded:
        df = st.session_state.df
        st.dataframe(df)
        visualizacion_pro(df)
    else:
        st.info("Esperando que se carguen los datos por otro usuario...")

# --- Cierre de sesión ---
if st.sidebar.button("🔓 Cerrar sesión"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# --- Flujo Principal ---
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.role == "admin":
        admin_panel()
    elif st.session_state.role == "tecnico":
        tecnico_panel()
    elif st.session_state.role == "observador":
        observador_panel()
            
