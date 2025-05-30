hydromet_pro_app.py

Sistema completo con roles, autenticación, funcionalidades avanzadas y estilo profesional

Este es un esqueleto base extendido de la aplicación para ser escalado y funcional 100%

import streamlit as st import pandas as pd import numpy as np import datetime from io import BytesIO from fpdf import FPDF from docx import Document import base64

-------- CONFIGURACIÓN INICIAL --------

st.set_page_config(page_title="HydroClimaPro", layout="wide")

st.markdown(""" <style> .main { background-color: #f7f9fc; } .css-1d391kg { padding: 2rem 3rem; } .report-title { font-size: 24px; font-weight: bold; color: #143d59; } .data-label { font-weight: bold; color: #333; } .section-header { font-size: 20px; color: #275dad; margin-top: 30px; } .btn-download { background-color: #143d59; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; } </style> """, unsafe_allow_html=True)

-------- SISTEMA DE USUARIOS SIMPLIFICADO --------

usuarios = { "tecnico": {"password": "1234", "rol": "Técnico de Campo"}, "analista": {"password": "5678", "rol": "Analista"}, "supervisor": {"password": "admin1", "rol": "Supervisor"}, "admin": {"password": "admin", "rol": "Administrador"}, }

if "usuario" not in st.session_state: st.session_state.usuario = None

-------- LOGIN --------

if not st.session_state.usuario: st.title("🔐 Inicio de sesión") user = st.text_input("Usuario") pwd = st.text_input("Contraseña", type="password") if st.button("Iniciar sesión"): if user in usuarios and usuarios[user]["password"] == pwd: st.session_state.usuario = user st.rerun() else: st.error("Credenciales incorrectas") st.stop()

rol = usuarios[st.session_state.usuario]["rol"] st.sidebar.success(f"Usuario: {st.session_state.usuario} ({rol})")

-------- MENÚ LATERAL --------

opcion = st.sidebar.radio("Menú", [ "Inicio", "Importar Datos", "Visualizar & Filtrar", "Reportes", "Mapa de Estaciones", "Bitácoras" if rol != "Técnico de Campo" else None, "Administración" if rol == "Administrador" else None ])

-------- FUNCIONES UTILES --------

def generar_pdf(df): pdf = FPDF() pdf.add_page() pdf.set_font("Arial", size=12) pdf.cell(200, 10, txt="Reporte Hidrometeorológico", ln=1, align="C") for i, row in df.iterrows(): pdf.cell(200, 10, txt=f"{row.to_dict()}", ln=1) buffer = BytesIO() pdf.output(buffer) buffer.seek(0) return buffer

def generar_word(df): doc = Document() doc.add_heading("Reporte Hidrometeorológico", 0) table = doc.add_table(rows=1, cols=len(df.columns)) hdr_cells = table.rows[0].cells for i, col in enumerate(df.columns): hdr_cells[i].text = col for _, row in df.iterrows(): row_cells = table.add_row().cells for i, val in enumerate(row): row_cells[i].text = str(val) buffer = BytesIO() doc.save(buffer) buffer.seek(0) return buffer

-------- INICIO --------

if opcion == "Inicio": st.title("🌧️ HydroClimaPro") st.markdown(f"Bienvenido {st.session_state.usuario}, rol: {rol}") st.markdown("""Esta plataforma te permite importar, visualizar, analizar y generar reportes sobre datos hidrológicos y meteorológicos de manera eficiente.")

-------- IMPORTAR DATOS --------

elif opcion == "Importar Datos": st.title("📥 Importar Datos") archivo = st.file_uploader("Sube un archivo (.csv, .xlsx, .json)", type=["csv", "xlsx", "json"]) if archivo: try: if archivo.name.endswith(".csv"): df = pd.read_csv(archivo) elif archivo.name.endswith(".xlsx"): df = pd.read_excel(archivo) elif archivo.name.endswith(".json"): df = pd.read_json(archivo) else: st.warning("Formato no soportado") st.session_state.df = df st.success("Archivo cargado correctamente") except Exception as e: st.error(f"Error: {e}")

-------- VISUALIZAR Y FILTRAR --------

elif opcion == "Visualizar & Filtrar": st.title("🔍 Visualizar y Filtrar Datos") if "df" in st.session_state: df = st.session_state.df st.dataframe(df)

with st.expander("Filtrar por columna"):
        columnas = st.multiselect("Selecciona columnas", df.columns)
        if columnas:
            st.dataframe(df[columnas])

    st.markdown("""---""")
    st.subheader("📤 Exportar")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Descargar PDF"):
            try:
                buffer = generar_pdf(df)
                st.download_button("Descargar PDF", buffer, file_name="reporte.pdf")
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")

    with col2:
        if st.button("📝 Descargar Word"):
            try:
                buffer = generar_word(df)
                st.download_button("Descargar Word", buffer, file_name="reporte.docx")
            except Exception as e:
                st.error(f"Error al generar Word: {e}")
else:
    st.warning("Primero importa un archivo")

-------- REPORTES --------

elif opcion == "Reportes": st.title("📑 Generador de Reportes") st.info("Esta sección está en desarrollo para incluir plantillas predefinidas de reportes técnicos y comparativos.")

-------- MAPA --------

elif opcion == "Mapa de Estaciones": st.title("🗺️ Mapa de Estaciones") st.info("Módulo en construcción para integrar datos geoespaciales y estaciones climáticas")

-------- BITÁCORAS --------

elif opcion == "Bitácoras" and rol != "Técnico de Campo": st.title("📝 Registro de Bitácoras") st.text_area("Describe tu observación de campo") st.button("Guardar Bitácora")

-------- ADMINISTRACION --------

elif opcion == "Administración" and rol == "Administrador": st.title("🔐 Panel de Administración") st.info("Desde aquí podrás gestionar usuarios, configuraciones del sistema y más.")

