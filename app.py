import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
from docx import Document
from fpdf import FPDF
import seaborn as sns
import matplotlib.pyplot as plt

# ------------------------- CONFIGURACIÓN DE LA PÁGINA -------------------------
st.set_page_config(page_title="HydroClima Ultra PRO", layout="wide")

# ------------------------- SESIÓN DE USUARIO -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.rol = ""

# ------------------------- BASE DE USUARIOS -------------------------
users_db = {
    "admin": {"password": "admin123", "rol": "admin"},
    "tecnico": {"password": "tec123", "rol": "tecnico"},
    "analista": {"password": "ana123", "rol": "analista"},
}

# ------------------------- FUNCIONES AUXILIARES -------------------------
def login():
    st.title("🔐 Acceso a HydroClima PRO")
    st.write("Por favor, introduce tus credenciales para acceder al sistema.")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if username in users_db and users_db[username]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.rol = users_db[username]["rol"]
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.rol = ""
    st.experimental_rerun()

# ------------------------- DASHBOARDS POR ROL -------------------------
def admin_dashboard():
    st.sidebar.title("👑 Panel de Administración")
    st.sidebar.button("Cerrar sesión", on_click=logout)

    st.title("HydroClima Ultra PRO - Panel Administrador")
    uploaded_file = st.file_uploader("Sube un archivo CSV de sensores", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("Archivo cargado correctamente")

        st.subheader("📊 Vista previa de los datos")
        st.dataframe(df.head(), use_container_width=True)

        st.subheader("📉 Análisis estadístico general")
        st.dataframe(df.describe(), use_container_width=True)

        st.subheader("📈 Gráficos avanzados")
        columnas_numericas = df.select_dtypes(include=np.number).columns.tolist()
        selected_col = st.selectbox("Selecciona una columna para graficar", columnas_numericas)

        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df[selected_col], mode='lines+markers', name=selected_col))
        fig.update_layout(template="plotly_dark", title=f"Tendencia de {selected_col}")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📤 Exportar informe")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Descargar informe Word"):
                doc = Document()
                doc.add_heading("Informe Hidrometeorológico", 0)
                doc.add_paragraph(f"Generado por: {st.session_state.username} ({st.session_state.rol})")
                doc.add_paragraph(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                doc.add_paragraph("\nResumen Estadístico:")
                for col in columnas_numericas:
                    doc.add_paragraph(f"{col}: Media={df[col].mean():.2f}, Máx={df[col].max()}, Mín={df[col].min()}")
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                st.download_button(
                    label="📄 Descargar Word",
                    data=buffer,
                    file_name="informe.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        with col2:
            if st.button("Descargar informe PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
                pdf.ln(10)
                pdf.cell(200, 10, txt=f"Usuario: {st.session_state.username}", ln=True)
                for col in columnas_numericas:
                    stats = f"{col} - Media: {df[col].mean():.2f}, Máx: {df[col].max()}, Mín: {df[col].min()}"
                    pdf.cell(200, 10, txt=stats, ln=True)
                pdf_output = BytesIO()
                pdf.output(pdf_output)
                pdf_output.seek(0)
                st.download_button(
                    label="📑 Descargar PDF",
                    data=pdf_output,
                    file_name="informe.pdf",
                    mime="application/pdf"
                )

        st.subheader("📡 Simulación de conexión a sensores")
        st.info("Conexión establecida con sensores. Datos actualizados en tiempo real.")
        st.code("Conectado al sensor ID_001: Temp=25.4°C, Humedad=61%", language="text")

        st.subheader("🧑‍💼 Gestión de usuarios (solo simulación)")
        st.json(users_db)

    else:
        st.warning("Por favor, sube un archivo CSV para comenzar.")

def tecnico_dashboard():
    st.sidebar.title("🔧 Panel Técnico")
    st.sidebar.button("Cerrar sesión", on_click=logout)
    st.title("Panel Técnico de Monitoreo")
    st.write("(Funciones específicas para técnicos en campo, revisión rápida de sensores)")

def analista_dashboard():
    st.sidebar.title("📈 Panel de Analista")
    st.sidebar.button("Cerrar sesión", on_click=logout)
    st.title("Panel de Analista de Datos")
    st.write("(Herramientas avanzadas de interpretación, predicción e informes de datos)")

# ------------------------- INICIO -------------------------
if not st.session_state.authenticated:
    login()
else:
    if st.session_state.rol == "admin":
        admin_dashboard()
    elif st.session_state.rol == "tecnico":
        tecnico_dashboard()
    elif st.session_state.rol == "analista":
        analista_dashboard()
    
