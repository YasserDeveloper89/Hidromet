import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime

# --- Configuración de la página ---
st.set_page_config(page_title="HydroClima PRO", layout="wide")

# --- Datos de usuarios ---
USERS = {
    "admin": {"password": "admin123", "role": "Administrador"},
    "tecnico": {"password": "tecnico123", "role": "Técnico"},
    "observador": {"password": "observador123", "role": "Observador"}
}

# --- Inicializar sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- Funciones de exportación ---
def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos", ln=1, align="C")
        for i in range(len(df)):
            row = ', '.join([str(x) for x in df.iloc[i]])
            pdf.cell(200, 10, txt=row, ln=1)
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        st.download_button("📄 Descargar PDF", buffer, file_name="informe.pdf")
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
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        st.download_button("📝 Descargar Word", buffer, file_name="informe.docx")
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

# --- Dashboard por rol ---
def admin_panel(df):
    st.title("Panel de Administración")
    st.success("Acceso total garantizado ✅")
    st.subheader("📈 Gráficos interactivos")
    if df is not None:
        for col in df.select_dtypes(include=np.number).columns:
            fig = px.line(df, y=col, title=f"Evolución de {col}", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📤 Exportar informes")
        export_pdf(df)
        export_word(df)

        st.subheader("🛠️ Herramientas avanzadas")
        st.write("- Conexión a dispositivos de medición (simulada)")
        st.write("- Control de accesos")
        st.write("- Gestión de logs de uso")
    else:
        st.warning("Carga un archivo primero para acceder a todas las funciones.")

def tecnico_panel(df):
    st.title("Panel Técnico")
    st.subheader("📊 Visualización de datos")
    if df is not None:
        st.dataframe(df.head())
        selected_col = st.selectbox("Selecciona columna numérica para graficar", df.select_dtypes(include=np.number).columns)
        st.plotly_chart(px.line(df, y=selected_col, title=f"Gráfico de {selected_col}", template="plotly_dark"), use_container_width=True)
        export_pdf(df)
    else:
        st.warning("Por favor, carga un archivo CSV.")

def observador_panel(df):
    st.title("Panel de Observación")
    if df is not None:
        st.dataframe(df.head(10))
    else:
        st.warning("Carga un archivo para visualizar.")

# --- Login ---
def login():
    st.title("🔐 Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.success(f"Bienvenido, {username} ({st.session_state.role})")
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas")

# --- Logout ---
def logout():
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.experimental_rerun()

# --- Carga de archivo CSV ---
def cargar_archivo():
    st.sidebar.subheader("📁 Cargar archivo CSV")
    archivo = st.sidebar.file_uploader("Selecciona un archivo", type=["csv"])
    if archivo:
        df = pd.read_csv(archivo)
        return df
    return None

# --- Ejecución principal ---
if not st.session_state.logged_in:
    login()
else:
    logout()
    df = cargar_archivo()
    role = st.session_state.role
    if role == "Administrador":
        admin_panel(df)
    elif role == "Técnico":
        tecnico_panel(df)
    elif role == "Observador":
        observador_panel(df)
