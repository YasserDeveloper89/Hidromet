# --- Page config must be first ---
import streamlit as st
st.set_page_config(page_title="HydroClima PRO", layout="wide")

# --- Imports ---
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import base64

# --- Sample Users DB ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tec123", "role": "tecnico"},
    "analista": {"password": "ana123", "role": "analista"}
}

# --- Simulated Sensor Data ---
def get_sensor_data():
    dates = pd.date_range(end=datetime.today(), periods=30)
    data = {
        "Fecha": dates,
        "Temperatura (°C)": np.random.uniform(15, 35, size=30),
        "Precipitación (mm)": np.random.uniform(0, 20, size=30),
        "Humedad (%)": np.random.uniform(40, 90, size=30),
    }
    return pd.DataFrame(data)

# --- Auth Management ---
def login():
    st.title("HydroClima PRO - Acceso")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state["auth"] = True
            st.session_state["user"] = username
            st.session_state["role"] = user["role"]
        else:
            st.error("Credenciales incorrectas")

# --- Export PDF ---
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos Climáticos", ln=True, align='C')
    pdf.ln()
    for i, row in df.iterrows():
        row_data = ", ".join([f"{col}: {row[col]}" for col in df.columns])
        pdf.multi_cell(0, 10, row_data)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    st.download_button("Descargar PDF", data=pdf_output.getvalue(), file_name="informe.pdf")

# --- Export Word ---
def export_word(df):
    doc = Document()
    doc.add_heading("Informe de Datos Climáticos", level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, col in enumerate(df.columns):
            row_cells[i].text = str(row[col])
    word_output = BytesIO()
    doc.save(word_output)
    st.download_button("Descargar Word", data=word_output.getvalue(), file_name="informe.docx")

# --- Dashboard ---
def admin_panel():
    st.subheader("Panel de Administrador")
    df = get_sensor_data()
    st.write("### Vista Previa de Datos")
    st.dataframe(df)

    st.write("### Análisis Estadístico")
    st.dataframe(df.describe())

    st.write("### Visualización Avanzada")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["Temperatura (°C)"], mode='lines+markers', name='Temp', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["Precipitación (mm)"], mode='lines+markers', name='Lluvia', line=dict(color='blue')))
    fig.update_layout(template="plotly_dark", title="Condiciones Climáticas", xaxis_title="Fecha", yaxis_title="Valor")
    st.plotly_chart(fig, use_container_width=True)

    st.write("### Generar Informes")
    col1, col2 = st.columns(2)
    with col1:
        export_pdf(df)
    with col2:
        export_word(df)

    st.write("### Gestión de Usuarios (Simulada)")
    st.info("Aquí se podría integrar la creación y eliminación de usuarios en producción.")

# --- Technician ---
def tecnico_panel():
    st.subheader("Panel Técnico")
    df = get_sensor_data()
    st.dataframe(df)
    st.write("### Gráfico de Temperatura")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Fecha"], y=df["Temperatura (°C)"], marker_color="indianred"))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- Analyst ---
def analista_panel():
    st.subheader("Panel Analista")
    df = get_sensor_data()
    st.dataframe(df.head(10))
    st.write("### Descargar Informes")
    export_pdf(df)
    export_word(df)

# --- Main ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    login()
else:
    user = st.session_state["user"]
    role = st.session_state["role"]
    st.sidebar.success(f"Bienvenido, {user} ({role})")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    st.title("HydroClima PRO - Panel Principal")
    if role == "admin":
        admin_panel()
    elif role == "tecnico":
        tecnico_panel()
    elif role == "analista":
        analista_panel()
