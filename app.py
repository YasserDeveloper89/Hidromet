# Versión Premium Pro - Aplicación Hidrometeorológica

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from fpdf import FPDF
from docx import Document
from datetime import datetime
import base64
import seaborn as sns
import matplotlib.pyplot as plt

# --- Configuración inicial ---
st.set_page_config(page_title="HydroClimaPRO Admin Dashboard", layout="wide")

# --- Variables de sesión ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''

# --- Base de datos simulada de usuarios ---
users_db = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tec123", "role": "tecnico"},
    "cliente": {"password": "cliente123", "role": "cliente"}
}

# --- Funciones auxiliares ---
def generate_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=True, align='C')
        pdf.ln(10)

        col_names = df.columns.tolist()
        header = ' | '.join(col_names)
        pdf.multi_cell(0, 10, header)

        for _, row in df.iterrows():
            row_text = ' | '.join([str(x) for x in row.tolist()])
            pdf.multi_cell(0, 10, row_text)

        pdf_output = f"informe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as f:
            st.download_button("🔖 Descargar PDF", f, file_name=pdf_output)
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

def generate_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe de Datos Hidrometeorológicos", 0)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col_name in enumerate(df.columns):
            hdr_cells[i].text = col_name
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, value in enumerate(row):
                row_cells[i].text = str(value)
        word_output = f"informe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        doc.save(word_output)
        with open(word_output, "rb") as f:
            st.download_button("🔖 Descargar Word", f, file_name=word_output)
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.experimental_rerun()

# --- Login ---
def login():
    with st.form("login_form"):
        st.markdown("## Iniciar Sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login_button = st.form_submit_button("Iniciar sesión")

        if login_button:
            user = users_db.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Bienvenido, {username}")
                st.experimental_rerun()
            else:
                st.error("Credenciales inválidas")

# --- Panel Admin ---
def admin_panel():
    st.title("💻 Panel del Administrador - HydroClimaPRO")
    st.markdown("### Módulo de control total")
    st.button("Cerrar sesión", on_click=logout)

    st.subheader("📂 Carga de Datos")
    data_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

    if data_file is not None:
        df = pd.read_csv(data_file)
        st.dataframe(df, use_container_width=True)

        st.subheader("💡 Estadísticas Descriptivas")
        st.write(df.describe())

        st.subheader("📈 Gráficos de Dispersión")
        columnas = df.columns.tolist()
        x = st.selectbox("Eje X", columnas)
        y = st.selectbox("Eje Y", columnas, index=1)
        fig = px.scatter(df, x=x, y=y, title=f"{x} vs {y}", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🔄 Mapa de Correlación")
        try:
            fig_corr = px.imshow(df.corr(numeric_only=True), text_auto=True, aspect="auto")
            st.plotly_chart(fig_corr, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo generar el mapa de correlación: {e}")

        st.subheader("🔖 Exportar Informes")
        generate_pdf(df)
        generate_word(df)

        # Placeholder para las 10 funcionalidades extra (análisis en tiempo real, predicción, etc)
        st.markdown("---")
        st.subheader("🌍 Conexión a Sensores en Tiempo Real")
        st.info("Simulación: Obteniendo datos en tiempo real desde sensores...")
        realtime_data = df.sample(1)
        st.write(realtime_data)

        # Aquí se podrían incluir más módulos como:
        # - Comparación entre estaciones
        # - Dashboard meteorológico
        # - Análisis de series temporales
        # - Módulo de alertas
        # - Sistema de reportes automáticos

# --- Aplicación principal ---
if not st.session_state.logged_in:
    login()
else:
    user = users_db.get(st.session_state.username)
    if user:
        if user["role"] == "admin":
            admin_panel()
        else:
            st.warning("El panel para este tipo de usuario está en desarrollo.")
        
