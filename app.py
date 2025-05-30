import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from docx import Document
from fpdf import FPDF

st.set_page_config(page_title="HydroClima PRO", layout="wide")

# --- Definición de usuarios ---
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
    st.session_state.trigger_login = False

# --- Exportar PDF ---
def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos", ln=1, align="C")
        for i in range(len(df)):
            row = ', '.join([str(x) for x in df.iloc[i]])
            pdf.cell(200, 10, txt=row, ln=1)

        pdf_bytes = pdf.output(dest="S").encode("latin1")
        st.download_button("📄 Descargar PDF", data=pdf_bytes, file_name="informe.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

# --- Exportar Word ---
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

# --- Paneles de usuario ---
def admin_panel(df):
    st.title("👑 Panel de Administración")
    if df is not None:
        st.subheader("📈 Análisis avanzado")
        for col in df.select_dtypes(include=np.number).columns:
            fig = px.line(df, y=col, title=f"Evolución de {col}", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📤 Exportar")
        export_pdf(df)
        export_word(df)

        st.subheader("⚙️ Control del sistema")
        st.markdown("✅ Conexión a sensores (modo simulado)")
        st.markdown("✅ Gestión total de datos")
    else:
        st.info("Carga un archivo CSV para acceder a las funciones.")

def tecnico_panel(df):
    st.title("🧪 Panel Técnico")
    if df is not None:
        st.dataframe(df.head())
        selected_col = st.selectbox("Columna para graficar", df.select_dtypes(include=np.number).columns)
        st.plotly_chart(px.line(df, y=selected_col, title=f"{selected_col}", template="plotly_dark"), use_container_width=True)
        export_pdf(df)
    else:
        st.warning("Carga un archivo para visualizar datos.")

def observador_panel(df):
    st.title("👁️ Panel Observador")
    if df is not None:
        st.dataframe(df.head(10))
    else:
        st.warning("Carga un archivo para visualizar datos.")

# --- Interfaz de Login ---
def login_ui():
    st.title("🔐 Inicia sesión para acceder")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
        else:
            st.error("❌ Usuario o contraseña incorrectos")

# --- Logout ---
def logout():
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

# --- Subida de archivo ---
def cargar_csv():
    st.sidebar.subheader("📂 Cargar datos")
    archivo = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])
    if archivo:
        return pd.read_csv(archivo)
    return None

# --- App principal ---
if not st.session_state.logged_in:
    login_ui()
else:
    st.sidebar.success(f"👤 {st.session_state.username} ({st.session_state.role})")
    logout()
    df = cargar_csv()

    rol = st.session_state.role
    if rol == "Administrador":
        admin_panel(df)
    elif rol == "Técnico":
        tecnico_panel(df)
    elif rol == "Observador":
        observador_panel(df)
