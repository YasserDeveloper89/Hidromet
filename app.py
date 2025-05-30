import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

# ---- CONFIGURACIÓN DE PÁGINA ----
st.set_page_config(page_title="HydroClimaPRO", layout="wide")

# ---- SESIÓN Y CONTROL DE ROL ----
if "rol" not in st.session_state:
    st.session_state["rol"] = None

st.markdown("# HydroClimaPRO 🌊 - Plataforma Profesional de Datos Climáticos")
st.markdown("""
<style>
    .main {background-color: #f5f7fa; font-family: 'Segoe UI', sans-serif;}
    h1, h2, h3 {color: #1a1a1a;}
</style>
""", unsafe_allow_html=True)

# ---- SIMULADOR DE LOGIN POR ROL ----
rol = st.sidebar.selectbox("Selecciona tu rol:", ["Seleccionar", "Técnico", "Supervisor", "Administrador"])
if rol != "Seleccionar":
    st.session_state["rol"] = rol

# ---- CARGA DE DATOS ----
st.sidebar.header("Sube tus datos")
archivo = st.sidebar.file_uploader("Archivo CSV", type=["csv"])
df = None
if archivo:
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip()

# ---- MENÚ LATERAL ----
if st.session_state["rol"]:
    menu = st.sidebar.radio("Menú", ["Inicio", "Visualización de Datos", "Análisis Avanzado", "Generar Informe"])

    # ---- INICIO ----
    if menu == "Inicio":
        st.subheader(f"Bienvenido, {st.session_state['rol']}")
        st.info("Cargue datos en formato CSV desde la barra lateral para comenzar.")

        if st.session_state["rol"] == "Administrador":
            st.success("Acceso completo a todos los módulos.")

    # ---- VISUALIZACIÓN DE DATOS ----
    if menu == "Visualización de Datos" and df is not None:
        st.subheader("📊 Visualización de Datos")

        col = st.selectbox("Selecciona una columna numérica:", df.select_dtypes(include=np.number).columns)
        if col:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines+markers', name=col))
            fig.update_layout(template="plotly_dark", title=f"Evolución de {col}")
            st.plotly_chart(fig, use_container_width=True)

    # ---- ANÁLISIS AVANZADO ----
    if menu == "Análisis Avanzado" and df is not None and st.session_state["rol"] != "Técnico":
        st.subheader("📈 Herramientas Avanzadas")

        col = st.selectbox("Variable para análisis estadístico:", df.select_dtypes(include=np.number).columns)
        if col:
            st.write("**Resumen estadístico:**")
            st.dataframe(df[col].describe())

            st.write("**Tendencia simple:**")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name='Data'))
            z = np.polyfit(df.index, df[col], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(x=df.index, y=p(df.index), mode='lines', name='Tendencia'))
            fig.update_layout(template="plotly_white", title="Tendencia")
            st.plotly_chart(fig, use_container_width=True)

    # ---- GENERACIÓN DE INFORME ----
    if menu == "Generar Informe" and df is not None:
        st.subheader("📝 Generar Informe PDF / Word")

        informe = st.text_area("Resumen del Informe:", "Descripción general del comportamiento climático registrado...")

        if st.button("Generar Documento"):
            # Word
            doc = Document()
            doc.add_heading("Informe de Datos Climáticos", level=1)
            doc.add_paragraph(informe)
            doc.add_paragraph("\nTabla de datos:")
            t = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = t.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = col
            for _, row in df.iterrows():
                row_cells = t.add_row().cells
                for i, cell in enumerate(row):
                    row_cells[i].text = str(cell)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_climatico.docx">📥 Descargar Informe Word</a>'
            st.markdown(href, unsafe_allow_html=True)

            # PDF
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, f"Resumen:\n{informe}\n\n")
                for i, row in df.iterrows():
                    row_data = ", ".join(str(x) for x in row)
                    pdf.multi_cell(0, 10, row_data)
                pdf_buffer = BytesIO()
                pdf.output(pdf_buffer)
                pdf_buffer.seek(0)
                b64_pdf = base64.b64encode(pdf_buffer.read()).decode()
                href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="informe_climatico.pdf">📥 Descargar Informe PDF</a>'
                st.markdown(href_pdf, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")
else:
    st.warning("Por favor, selecciona tu rol en la barra lateral para comenzar.")


He actualizado la versión premium PRO Ultra de la aplicación “HydroClimaPRO” con:

Interfaz refinada y profesional.

Control de acceso por rol (Técnico, Supervisor, Administrador).

Visualización gráfica avanzada con Plotly en estilo oscuro.

Herramientas de análisis estadístico y regresión lineal.

Generación de informes en PDF y Word desde Streamlit.

Corrección completa de errores de sintaxis.


¿Quieres que incorpore nuevas fuentes de datos en tiempo real (por ejemplo, vía APIs de estaciones climáticas)? También podemos trabajar en un panel administrativo avanzado con autenticación.

