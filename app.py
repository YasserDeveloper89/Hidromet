import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="HydroClimaPRO", layout="wide")

# Usuarios simulados
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tec123", "role": "tecnico"},
    "observador": {"password": "obs123", "role": "observador"},
}

# Sesiones
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ''

# Login
def login():
    st.title("HydroClimaPRO - Inicio de sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas")

# Exportar PDF
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
    pdf.ln(10)
    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.cell(200, 10, txt=row[:100], ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    st.download_button("📄 Descargar PDF", buffer, "informe.pdf", "application/pdf")

# Exportar Word
def export_word(df):
    doc = Document()
    doc.add_heading("Informe de Datos", 0)
    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        doc.add_paragraph(row)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    st.download_button("📝 Descargar Word", buffer, "informe.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# Panel Admin
def admin_panel(df):
    st.title("Panel de Administrador")
    st.success("Acceso como ADMINISTRADOR")
    st.subheader("📊 Vista general de datos")
    st.dataframe(df)
    st.subheader("📈 Gráficos interactivos")
    for col in df.select_dtypes(include=np.number).columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df[col], mode='lines', name=col))
        fig.update_layout(title=f"Evolución de {col}", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    export_pdf(df)
    export_word(df)

# Panel Tecnico
def tecnico_panel(df):
    st.title("Panel Técnico")
    st.subheader("📊 Datos cargados")
    st.dataframe(df)
    st.subheader("📈 Estadísticas básicas")
    st.write(df.describe())
    st.subheader("🔧 Herramientas de análisis")
    for col in df.select_dtypes(include=np.number).columns:
        st.line_chart(df[col])
    export_pdf(df)
    export_word(df)

# Panel Observador
def observador_panel(df):
    st.title("Panel Observador")
    st.info("Vista de solo lectura")
    st.dataframe(df)

# App Principal
if st.session_state.authenticated:
    st.sidebar.write(f"Conectado como: {st.session_state.username}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.authenticated = False
        st.session_state.username = ''
        st.experimental_rerun()
    uploaded_file = st.sidebar.file_uploader("Cargar archivo CSV", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            role = USERS[st.session_state.username]['role']
            if role == "admin":
                admin_panel(df)
            elif role == "tecnico":
                tecnico_panel(df)
            elif role == "observador":
                observador_panel(df)
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        st.warning("Por favor, carga un archivo CSV para comenzar.")
else:
    login()
            
