import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime
import os

# --- Configuración de la página ---
st.set_page_config(page_title="Panel Hidromet PRO", layout="wide")

# --- Usuarios simulados ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tec123", "role": "tecnico"},
    "cliente": {"password": "cli123", "role": "cliente"}
}

# --- Inicializar estado de sesión ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.experimental_rerun()

def login():
    with st.form("login_form"):
        st.markdown("### Iniciar sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión")

        if submitted:
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.success(f"Bienvenido, {username}")
                st.experimental_rerun()
            else:
                st.error("Credenciales inválidas")

def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
        pdf.ln(10)

        col_width = pdf.w / (len(df.columns) + 1)
        for col in df.columns:
            pdf.cell(col_width, 10, col, border=1)
        pdf.ln()
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 10, str(item), border=1)
            pdf.ln()

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        st.download_button("Descargar PDF", data=pdf_output.getvalue(), file_name="informe.pdf")
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

def export_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe de Datos", 0)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = col

        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)

        word_output = BytesIO()
        doc.save(word_output)
        st.download_button("Descargar Word", data=word_output.getvalue(), file_name="informe.docx")
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

def admin_panel():
    st.title("Panel de Administrador")
    uploaded_file = st.file_uploader("Subir archivo de datos", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith("csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("Vista previa de los datos")
            st.dataframe(df)

            st.subheader("Descarga de informes")
            export_pdf(df)
            export_word(df)

            st.subheader("Estadísticas básicas")
            st.write(df.describe())

            st.subheader("Gráficos interactivos")
            try:
                numeric_df = df.select_dtypes(include=np.number)
                fig_corr = px.imshow(numeric_df.corr(), text_auto=True, aspect="auto")
                st.plotly_chart(fig_corr, use_container_width=True)
            except Exception as e:
                st.warning(f"Error al generar el mapa de correlación: {e}")

            st.subheader("Histograma")
            for column in numeric_df.columns:
                fig = px.histogram(df, x=column, nbins=30, title=f"Histograma de {column}")
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Conexión con sensores")
            st.info("(Simulado) Lectura de datos en tiempo real conectando con dispositivos externos...")

            # Más herramientas aquí...
            st.success("Herramientas cargadas exitosamente.")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        st.info("Por favor, sube un archivo para comenzar.")

def tecnico_panel():
    st.title("Panel Técnico")
    st.info("Carga de datos y análisis técnico disponible.")

def cliente_panel():
    st.title("Panel Cliente")
    st.info("Visualización de reportes disponibles.")

# --- Lógica principal ---
if not st.session_state.authenticated:
    login()
else:
    st.sidebar.title(f"Bienvenido {st.session_state.username}")
    st.sidebar.button("Cerrar sesión", on_click=logout)

    if st.session_state.role == "admin":
        admin_panel()
    elif st.session_state.role == "tecnico":
        tecnico_panel()
    elif st.session_state.role == "cliente":
        cliente_panel()
    else:
        st.error("Rol no reconocido.")
        
