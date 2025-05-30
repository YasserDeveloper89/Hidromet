import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

# ------------------------------
# ✅ Configurar página
# ------------------------------
st.set_page_config(page_title="HydroClima PRO+", layout="wide")

# ------------------------------
# 🔐 Definir usuarios y roles
# ------------------------------
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "supervisor": {"password": "super123", "role": "supervisor"},
    "tecnico": {"password": "tec123", "role": "tecnico"}
}

# ------------------------------
# 🌐 Manejo de sesión
# ------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None

# ------------------------------
# 🧪 Modo desarrollador (para probar otros roles sin login real)
# ------------------------------
with st.sidebar.expander("🔧 Modo desarrollador"):
    if st.button("Simular como Admin"):
        st.session_state.logged_in = True
        st.session_state.user_role = "admin"
        st.session_state.username = "admin"
    if st.button("Simular como Supervisor"):
        st.session_state.logged_in = True
        st.session_state.user_role = "supervisor"
        st.session_state.username = "supervisor"
    if st.button("Simular como Técnico"):
        st.session_state.logged_in = True
        st.session_state.user_role = "tecnico"
        st.session_state.username = "tecnico"

# ------------------------------
# 🔐 Login de usuario
# ------------------------------
if not st.session_state.logged_in:
    st.title("🔐 Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_role = USERS[username]["role"]
            st.session_state.username = username
            st.success(f"Bienvenido {username}! Rol: {st.session_state.user_role}")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

# ------------------------------
# 📁 Carga de archivo CSV
# ------------------------------
st.sidebar.title("📂 Archivo de datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file is None:
    st.info("Por favor, carga un archivo CSV para comenzar.")
    st.stop()

# ------------------------------
# 📊 Visualización de datos
# ------------------------------
data = pd.read_csv(uploaded_file)
st.title("HydroClima PRO+ - Panel de Análisis")
st.subheader(f"Bienvenido, {st.session_state.username.title()} ({st.session_state.user_role})")

st.markdown("---")
st.write("### Vista previa de datos")
st.dataframe(data, use_container_width=True)

# ------------------------------
# 📈 Gráfico principal (estilo PRO)
# ------------------------------
st.write("### Visualización avanzada")
columns = list(data.select_dtypes(include=[np.number]).columns)
col_x = st.selectbox("Eje X", options=data.columns)
col_y = st.selectbox("Eje Y (solo numéricos)", options=columns)

if col_y:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data[col_x], y=data[col_y], mode='lines+markers', line=dict(color='cyan')))
    fig.update_layout(template='plotly_dark', title="Visualización de Datos", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# 📄 Exportar informes (PDF y Word)
# ------------------------------
def generar_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos - HydroClima", ln=True, align="C")
    pdf.ln(10)
    for col in datos.columns:
        pdf.cell(200, 10, txt=f"{col}: {datos[col].iloc[0]}", ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def generar_docx(datos):
    doc = Document()
    doc.add_heading("Informe HydroClima", 0)
    table = doc.add_table(rows=1, cols=len(datos.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(datos.columns):
        hdr_cells[i].text = col
    row_cells = table.add_row().cells
    for i, val in enumerate(datos.iloc[0]):
        row_cells[i].text = str(val)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.markdown("---")
st.write("### Exportar informe")
if st.button("📄 Generar y descargar informe"):
    pdf_buffer = generar_pdf(data)
    docx_buffer = generar_docx(data)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(label="⬇️ Descargar PDF", data=pdf_buffer, file_name="informe_hydroclima.pdf", mime="application/pdf")
    with col2:
        st.download_button(label="⬇️ Descargar Word", data=docx_buffer, file_name="informe_hydroclima.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# ------------------------------
# 🧭 Funciones exclusivas por rol
# ------------------------------
if st.session_state.user_role == "admin":
    st.markdown("---")
    st.subheader("🛠 Herramientas de Administración")
    st.write("- Gestión de usuarios (en desarrollo)")
    st.write("- Acceso total a todas las secciones")
    st.write("- Visualización de logs de actividad (proximamente)")

elif st.session_state.user_role == "supervisor":
    st.markdown("---")
    st.subheader("📋 Panel del Supervisor")
    st.write("- Ver informes enviados")
    st.write("- Aprobaciones y observaciones")

elif st.session_state.user_role == "tecnico":
    st.markdown("---")
    st.subheader("🔧 Herramientas para Técnicos")
    st.write("- Registro de mediciones")
    st.write("- Subida de datos")

# ------------------------------
# 🔚 Cerrar sesión
# ------------------------------
if st.sidebar.button("Cerrar sesión"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
