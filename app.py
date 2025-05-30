import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

# --------------------------
# CONFIGURACIÓN INICIAL
# --------------------------
st.set_page_config(page_title="HydroClima PRO", layout="wide")

# --------------------------
# CREDENCIALES DE USUARIO
# --------------------------
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "analista": {"password": "analista123", "role": "analyst"},
    "tecnico": {"password": "tecnico123", "role": "technician"}
}

# --------------------------
# FUNCIONES DE SESIÓN
# --------------------------
def login():
    st.title("🔒 Iniciar sesión")
    st.markdown("Bienvenido a HydroClima PRO. Introduce tus credenciales para continuar.")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión")

        if submitted:
            if username in USERS and USERS[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = USERS[username]["role"]
                st.success("Login exitoso. Bienvenido, {}".format(username))
            else:
                st.error("Credenciales inválidas. Intenta de nuevo.")

# --------------------------
# BARRA SUPERIOR
# --------------------------
def top_bar():
    st.sidebar.title("📂 Menú")
    st.sidebar.write("**Usuario:**", st.session_state["username"])
    st.sidebar.write("**Rol:**", st.session_state["role"])
    if st.sidebar.button("🔚 Cerrar sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# --------------------------
# FUNCIONES DEL ADMIN
# --------------------------
def admin_dashboard():
    st.header("Panel de Administrador")
    st.markdown("Acceso completo al sistema, gestión de usuarios y más.")

    st.subheader("📈 Conexión con sensores en tiempo real (simulado)")
    if st.button("📡 Obtener datos del sensor de temperatura"):
        sensor_data = round(np.random.uniform(18, 30), 2)
        st.success(f"🌡️ Temperatura registrada: {sensor_data} °C")

    st.subheader("📊 Subida y análisis de datos")
    uploaded_file = st.file_uploader("Sube un archivo CSV con datos meteorológicos")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state["data"] = df
        st.dataframe(df)

        if st.button("📤 Exportar a PDF"):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Informe de Datos Meteorológicos", ln=1, align="C")
                for col in df.columns:
                    pdf.cell(200, 10, txt=f"{col}: {df[col].mean():.2f}", ln=1)
                pdf_output = BytesIO()
                pdf.output(pdf_output)
                st.download_button("⬇️ Descargar PDF", data=pdf_output.getvalue(), file_name="informe.pdf")
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")

# --------------------------
# FUNCIONES DEL ANALISTA
# --------------------------
def analyst_dashboard():
    st.header("Panel del Analista")
    st.markdown("Subida de archivos, análisis estadístico y visualización de datos.")

    uploaded_file = st.file_uploader("Sube un archivo CSV")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

        st.subheader("📊 Estadísticas básicas")
        st.write(df.describe())

        st.subheader("📈 Visualización interactiva")
        numeric_columns = df.select_dtypes(include=np.number).columns
        if len(numeric_columns) >= 2:
            x = st.selectbox("Eje X", numeric_columns)
            y = st.selectbox("Eje Y", numeric_columns, index=1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df[x], y=df[y], mode='markers', marker=dict(color='orange')))
            fig.update_layout(title=f"{y} vs {x}", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# --------------------------
# FUNCIONES DEL TÉCNICO
# --------------------------
def technician_dashboard():
    st.header("Panel del Técnico")
    st.markdown("Revisión de sensores, registros recientes y diagnósticos automáticos.")

    st.subheader("📟 Estado de sensores")
    st.info("Sensor A: OK\nSensor B: OK\nSensor C: OK")

    st.subheader("🔍 Diagnóstico rápido")
    st.success("Todos los sistemas operativos dentro de los parámetros esperados.")

# --------------------------
# MAIN
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    top_bar()
    role = st.session_state["role"]
    if role == "admin":
        admin_dashboard()
    elif role == "analyst":
        analyst_dashboard()
    elif role == "technician":
        technician_dashboard()
        
