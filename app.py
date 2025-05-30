import streamlit as st import pandas as pd import numpy as np from io import BytesIO from docx import Document from fpdf import FPDF import plotly.graph_objects as go import seaborn as sns import matplotlib.pyplot as plt import base64 from datetime import datetime

Configurar la página

st.set_page_config(page_title="HydroClimaPRO - Versión Administrador", layout="wide")

--- Simulación de usuarios ---

USERS = { "admin": {"password": "admin123", "role": "Administrador"}, "supervisor": {"password": "super123", "role": "Supervisor"}, "tecnico": {"password": "tec123", "role": "Técnico"}, }

if "logged_in" not in st.session_state: st.session_state.logged_in = False st.session_state.user_role = None

--- Autenticación ---

def login(): st.title("🔐 Inicio de sesión - HydroClimaPRO") username = st.text_input("Usuario") password = st.text_input("Contraseña", type="password") if st.button("Iniciar sesión"): if username in USERS and USERS[username]["password"] == password: st.session_state.logged_in = True st.session_state.user_role = USERS[username]["role"] st.success(f"Bienvenido, {username} ({st.session_state.user_role})") st.experimental_rerun() else: st.error("Credenciales inválidas")

if not st.session_state.logged_in: login() st.stop()

--- Funciones ---

def descargar_archivo(data, nombre, tipo): if tipo == "word": buffer = BytesIO() doc = Document() doc.add_heading("Informe de Datos Hidrometeorológicos", level=1) doc.add_paragraph(datetime.now().strftime("%d/%m/%Y %H:%M")) doc.add_paragraph("\nResumen de datos") t = doc.add_table(rows=1, cols=len(data.columns)) hdr_cells = t.rows[0].cells for i, col in enumerate(data.columns): hdr_cells[i].text = col for _, row in data.iterrows(): row_cells = t.add_row().cells for i, val in enumerate(row): row_cells[i].text = str(val) doc.save(buffer) st.download_button( label="📄 Descargar Word", data=buffer.getvalue(), file_name=f"{nombre}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" )

elif tipo == "pdf":
    buffer = BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
    pdf.cell(200, 10, txt=datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True, align="C")
    pdf.ln(10)
    for col in data.columns:
        pdf.cell(40, 10, col, border=1)
    pdf.ln()
    for _, row in data.iterrows():
        for item in row:
            pdf.cell(40, 10, str(item), border=1)
        pdf.ln()
    pdf.output(buffer)
    st.download_button(
        label="📄 Descargar PDF",
        data=buffer.getvalue(),
        file_name=f"{nombre}.pdf",
        mime="application/pdf"
    )

--- Carga de Datos ---

st.sidebar.title("📁 Datos") csv_file = st.sidebar.file_uploader("Sube tu archivo CSV", type="csv") if csv_file: df = pd.read_csv(csv_file) st.title("🌎 HydroClimaPRO - Plataforma de Análisis") st.subheader("📊 Vista previa de datos") st.dataframe(df.head())

# --- Análisis para Todos ---
st.subheader("📈 Visualización de Datos")
col = st.selectbox("Selecciona columna numérica", df.select_dtypes(include=np.number).columns)
fig = go.Figure()
fig.add_trace(go.Scatter(y=df[col], mode='lines+markers', name=col))
fig.update_layout(title=f"Tendencia de {col}", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# --- Estadísticas ---
st.subheader("📊 Estadísticas básicas")
st.write(df.describe())

# --- Exportar Informe ---
st.subheader("📤 Exportar informe")
nombre_archivo = st.text_input("Nombre del informe", value="informe_hidro")
descargar_archivo(df, nombre_archivo, tipo="pdf")
descargar_archivo(df, nombre_archivo, tipo="word")

# --- Funciones Exclusivas Admin ---
if st.session_state.user_role == "Administrador":
    st.subheader("🛠️ Panel de Administración Avanzado")
    st.markdown("- Conexión a sensores físicos o APIs de estaciones de medición")
    st.markdown("- Control de usuarios y permisos")
    st.markdown("- Módulo de alertas por eventos extremos")
    st.markdown("- Simulaciones climáticas futuras")
    st.markdown("- Exportación de reportes masivos")
    st.success("✅ Módulos avanzados activados")
    st.info("(Demo) Conexión a sensor: OK - Última actualización: 3 min")

else: st.warning("Por favor, sube un archivo CSV para comenzar.")

