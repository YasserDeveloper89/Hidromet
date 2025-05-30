import streamlit as st
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

# Configurar página Streamlit
theme = "HydroClimaPRO - Modo Admin"
st.set_page_config(page_title=theme, layout="wide")

# Variables de autenticación (para pruebas)
USUARIOS = {
    "admin": {"password": "admin123", "rol": "admin"},
    "supervisor": {"password": "super123", "rol": "supervisor"},
    "tecnico": {"password": "tec123", "rol": "tecnico"}
}

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None

def login():
    st.title("🔐 Iniciar sesión")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usuario in USUARIOS and USUARIOS[usuario]['password'] == contraseña:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas")

def cerrar_sesion():
    if st.sidebar.button("Cerrar sesión"):
        for k in ["autenticado", "usuario", "df"]:
            if k in st.session_state:
                del st.session_state[k]
        st.experimental_rerun()

def cargar_datos():
    archivo = st.file_uploader("📁 Cargar archivo CSV de datos", type="csv")
    if archivo:
        try:
            df = pd.read_csv(archivo)
            st.session_state.df = df
            st.success("Archivo cargado exitosamente")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

def vista_datos():
    df = st.session_state.get("df")
    if df is not None:
        st.subheader("👁 Vista previa de datos")
        st.dataframe(df, use_container_width=True)

def analisis_datos():
    df = st.session_state.get("df")
    if df is not None:
        st.subheader("📊 Análisis Estadístico Avanzado")
        desc = df.describe()
        st.dataframe(desc)

        st.markdown("---")
        col = st.selectbox("Selecciona una columna numérica para analizar:", df.select_dtypes(include=np.number).columns)
        if col:
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df[col], nbinsx=30, marker_color="#1f77b4"))
            fig.update_layout(title=f"Distribución de {col}", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        # Correlaciones
        corr = df.select_dtypes(include=np.number).corr()
        st.subheader("Mapa de Correlaciones")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

def generar_informe():
    df = st.session_state.get("df")
    if df is not None:
        st.subheader("📄 Generar Informe")
        resumen = st.text_area("Resumen del informe:", "Este es un informe generado automáticamente...")
        if st.button("Generar Informe"):
            try:
                # Word
                doc = Document()
                doc.add_heading("Informe de Datos Hidrometeorológicos", 0)
                doc.add_paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                doc.add_paragraph(resumen)
                doc.add_paragraph("\nTabla de Datos:")
                table = doc.add_table(rows=1, cols=len(df.columns))
                hdr_cells = table.rows[0].cells
                for i, col in enumerate(df.columns):
                    hdr_cells[i].text = str(col)
                for _, row in df.iterrows():
                    row_cells = table.add_row().cells
                    for i, val in enumerate(row):
                        row_cells[i].text = str(val)
                word_io = BytesIO()
                doc.save(word_io)
                word_io.seek(0)
                st.download_button("📥 Descargar informe Word", word_io, file_name="informe.docx")

                # PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
                pdf.multi_cell(0, 10, resumen)
                pdf.output("informe.pdf")
                with open("informe.pdf", "rb") as f:
                    st.download_button("📥 Descargar informe PDF", f, file_name="informe.pdf")
            except Exception as e:
                st.error(f"Ocurrió un error al generar el informe: {e}")

def funciones_admin():
    st.subheader("🔧 Panel de Administrador")
    st.info("Conexión con sensores externos activada. Recibiendo datos en tiempo real...")
    st.write("📡 Simulación de conexión con sensores de humedad y temperatura...")
    tiempo = st.slider("Intervalo de actualización (s)", 1, 10, 3)
    if st.button("Actualizar datos en vivo"):
        datos_live = {
            "Temperatura": np.round(np.random.normal(22, 2), 2),
            "Humedad": np.round(np.random.normal(65, 5), 2)
        }
        st.metric("🌡 Temperatura (°C)", datos_live["Temperatura"])
        st.metric("💧 Humedad (%)", datos_live["Humedad"])

def interfaz_usuario():
    st.sidebar.title(f"Bienvenido {st.session_state.usuario.title()}")
    cerrar_sesion()
    cargar_datos()

    if "df" in st.session_state:
        vista_datos()
        analisis_datos()
        generar_informe()

        # Funciones extra para admin
        if USUARIOS[st.session_state.usuario]["rol"] == "admin":
            funciones_admin()

# Ejecutar la app
if not st.session_state.autenticado:
    login()
else:
    interfaz_usuario()
      
