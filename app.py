# app.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import plotly.express as px
from fpdf import FPDF
from docx import Document
import base64
import time

# --- Configuración de página ---
st.set_page_config(page_title="HydroClima PRO Admin", layout="wide")

# --- Funciones auxiliares ---
def cargar_datos():
    uploaded_file = st.file_uploader("Cargar archivo de datos (CSV)", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state["data"] = df
        return df
    elif "data" in st.session_state:
        return st.session_state["data"]
    else:
        st.info("Por favor, cargue un archivo CSV.")
        return None

def exportar_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        col_width = 190 / len(df.columns)
        row_height = 8

        for col in df.columns:
            pdf.cell(col_width, row_height, col, border=1)
        pdf.ln(row_height)

        for i in range(min(len(df), 30)):
            for item in df.iloc[i]:
                pdf.cell(col_width, row_height, str(item), border=1)
            pdf.ln(row_height)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)

        st.download_button(
            label="📄 Descargar PDF",
            data=buffer,
            file_name="informe.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

def exportar_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe de Datos", level=1)
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

        st.download_button(
            label="📄 Descargar Word",
            data=buffer,
            file_name="informe.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

# --- Función simulada para sensores ---
def datos_sensores_simulados():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp": now,
        "temperatura": round(np.random.uniform(10, 40), 2),
        "humedad": round(np.random.uniform(30, 90), 2),
        "presion": round(np.random.uniform(950, 1050), 2),
    }

# --- Funciones para estadísticas ---
def mostrar_estadisticas(df):
    st.subheader("📊 Estadísticas descriptivas")
    st.write(df.describe())

def mostrar_graficos(df):
    st.subheader("📈 Gráficos interactivos")
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        fig = px.line(df, y=col, title=f"Serie temporal de {col}")
        st.plotly_chart(fig, use_container_width=True)

def correlaciones(df):
    st.subheader("📉 Matriz de correlación")
    corr = df.select_dtypes(include=np.number).corr()
    fig = px.imshow(corr, text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# --- Inicio de sesión ---
def login():
    with st.form("login_form"):
        st.markdown("### 🔐 Iniciar sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login_btn = st.form_submit_button("Iniciar sesión")

        if login_btn:
            if username == "admin" and password == "1234":
                st.session_state.usuario = "admin"
                st.experimental_rerun()
            else:
                st.error("Credenciales incorrectas.")

# --- Panel del Administrador ---
def panel_admin():
    st.title("Panel del Administrador 👨‍💼")

    tabs = st.tabs([
        "📂 Cargar datos", "📊 Estadísticas", "📈 Gráficos", "📉 Correlaciones", "🧲 Simulación Sensores",
        "📤 Exportar", "📅 Filtrado", "🧮 Variables derivadas", "🧼 Limpieza", "📚 Historial",
        "📋 Vista tabular", "📎 Archivos relacionados", "📍 Mapas", "📦 Modelado", "👥 Gestión de usuarios"
    ])

    df = cargar_datos()
    if df is not None:
        with tabs[1]: mostrar_estadisticas(df)
        with tabs[2]: mostrar_graficos(df)
        with tabs[3]: correlaciones(df)
        with tabs[4]:
            st.subheader("🧲 Datos en tiempo real (simulados)")
            if st.button("Actualizar lectura"):
                sensor_data = datos_sensores_simulados()
                st.write(sensor_data)
        with tabs[5]:
            exportar_pdf(df)
            exportar_word(df)
        with tabs[6]:
            st.dataframe(df)
            col = st.selectbox("Filtrar por columna:", df.columns)
            filtro = st.text_input("Valor a buscar")
            st.write(df[df[col].astype(str).str.contains(filtro)])
        with tabs[7]:
            st.write("Variables nuevas (demo)")
            df["media"] = df.select_dtypes(include=np.number).mean(axis=1)
            st.dataframe(df)
        with tabs[8]:
            st.write("Valores faltantes:")
            st.dataframe(df.isnull().sum())
        with tabs[9]:
            st.write("Historial de cargas (demo)")
        with tabs[10]:
            st.dataframe(df.head(50))
        with tabs[11]:
            st.write("Archivos relacionados (adjuntar PDFs, imágenes, etc.)")
        with tabs[12]:
            st.write("Visualización en mapa (próximamente)")
        with tabs[13]:
            st.write("Análisis de modelos predictivos (próximamente)")
        with tabs[14]:
            st.write("Gestión de usuarios (demo)")
            st.code("admin, tecnico, analista")

# --- Flujo Principal ---
if "usuario" not in st.session_state:
    login()
elif st.session_state.usuario == "admin":
    panel_admin()
else:
    st.warning("Usuario no autorizado para esta sección.")
        
