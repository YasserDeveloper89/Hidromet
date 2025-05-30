import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAR PÁGINA ---
st.set_page_config(page_title="HydroClimaPRO", layout="wide")

# --- BASE DE USUARIOS ---
USUARIOS = {
    "admin": {"password": "admin123", "role": "Administrador"},
    "supervisor": {"password": "super123", "role": "Supervisor"},
    "tecnico": {"password": "tec123", "role": "Técnico"},
}

# --- FUNCIONES DE SESIÓN ---
def login():
    st.sidebar.title("Inicio de sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Iniciar sesión"):
        user = USUARIOS.get(username)
        if user and user["password"] == password:
            st.session_state["logueado"] = True
            st.session_state["usuario"] = username
            st.session_state["rol"] = user["role"]
            st.experimental_rerun()
        else:
            st.sidebar.error("Credenciales inválidas")

# --- EXPORTACIÓN PDF ---
def exportar_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos Meteorológicos", ln=True, align="C")
    pdf.ln(10)

    for col in data.columns:
        pdf.cell(40, 10, col, border=1)
    pdf.ln()
    for _, row in data.iterrows():
        for val in row:
            pdf.cell(40, 10, str(val), border=1)
        pdf.ln()

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output

# --- EXPORTACIÓN WORD ---
def exportar_word(data):
    doc = Document()
    doc.add_heading("Informe de Datos Meteorológicos", 0)
    t = doc.add_table(rows=1, cols=len(data.columns))
    hdr_cells = t.rows[0].cells
    for i, col in enumerate(data.columns):
        hdr_cells[i].text = col
    for _, row in data.iterrows():
        row_cells = t.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    output = BytesIO()
    doc.save(output)
    return output

# --- GRÁFICO DETALLADO ---
def graficar(data):
    st.subheader("Visualización avanzada")
    for columna in data.select_dtypes(include=np.number).columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=data[columna], name=columna, mode="lines+markers"))
        fig.update_layout(title=f"Tendencia de {columna}", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- INTERFAZ PRINCIPAL ---
def app():
    st.title("HydroClimaPRO - Plataforma Meteorológica Profesional")
    st.markdown(f"### Bienvenido, {st.session_state['usuario']} ({st.session_state['rol']})")

    uploaded_file = st.file_uploader("Carga de archivo CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo cargado correctamente")

            st.subheader("Vista Previa de Datos")
            st.dataframe(df, use_container_width=True)

            if st.session_state['rol'] in ["Administrador", "Supervisor"]:
                graficar(df)

                st.markdown("### Exportar Informe")
                col1, col2 = st.columns(2)
                with col1:
                    pdf_bytes = exportar_pdf(df)
                    st.download_button("Descargar PDF", data=pdf_bytes.getvalue(), file_name="informe.pdf")
                with col2:
                    word_bytes = exportar_word(df)
                    st.download_button("Descargar Word", data=word_bytes.getvalue(), file_name="informe.docx")

            if st.session_state['rol'] == "Administrador":
                st.markdown("---")
                st.subheader("Panel de administración")
                st.info("Funcionalidades avanzadas como conexión directa a medidores, gestión de usuarios, configuración de sensores, etc. estarán disponibles aquí.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.warning("Por favor, carga un archivo CSV para comenzar.")

# --- MAIN ---
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    login()
else:
    app()
    
