import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO
from datetime import datetime
from docx import Document
from fpdf import FPDF
import plotly.express as px
import plotly.graph_objects as go

# Configurar la página
st.set_page_config(page_title="HydroClima PRO", layout="wide")

# Base de datos de usuarios
usuarios = {
    "admin": {"password": "admin123", "rol": "Administrador"},
    "tecnico": {"password": "tecnico123", "rol": "Técnico"},
    "cliente": {"password": "cliente123", "rol": "Cliente"}
}

# Variables de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol" not in st.session_state:
    st.session_state.rol = ""
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# Login
if not st.session_state.autenticado:
    st.title("🔐 Iniciar sesión en HydroClima PRO")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    login_btn = st.button("Iniciar sesión")
    if login_btn:
        if usuario in usuarios and usuarios[usuario]["password"] == contraseña:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.rol = usuarios[usuario]["rol"]
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas.")

else:
    rol = st.session_state.rol
    st.sidebar.write(f"👤 Usuario: {st.session_state.usuario} | Rol: {rol}")
    if st.sidebar.button("Cerrar sesión"):
        for key in ["autenticado", "rol", "usuario"]:
            st.session_state[key] = False if key == "autenticado" else ""
        st.experimental_rerun()

    if rol == "Administrador":
        st.title("👑 Panel del Administrador - HydroClima PRO")

        uploaded_file = st.file_uploader("📂 Cargar archivo de datos (CSV)", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success("Datos cargados correctamente")

            st.subheader("🔍 Vista previa de los datos")
            st.dataframe(df.head())

            # Función 1: Estadísticas generales
            st.subheader("📊 Estadísticas generales")
            st.write(df.describe())

            # Función 2: Gráfica de líneas para mediciones
            st.subheader("📈 Gráfico de Líneas")
            col = st.selectbox("Seleccionar columna para graficar:", df.columns)
            fig = px.line(df, y=col, title=f"Evolución de {col}")
            st.plotly_chart(fig, use_container_width=True)

            # Función 3: Histograma
            st.subheader("📊 Histograma")
            fig_hist = px.histogram(df, x=col, nbins=30, title=f"Histograma de {col}")
            st.plotly_chart(fig_hist, use_container_width=True)

            # Función 4: Mapa de calor de correlación
            st.subheader("🔥 Mapa de correlación")
            fig_corr = px.imshow(df.corr(), text_auto=True, aspect="auto")
            st.plotly_chart(fig_corr, use_container_width=True)

            # Función 5: Exportar a Word
            st.subheader("📄 Exportar Informe Word")
            def export_word(df):
                doc = Document()
                doc.add_heading("Informe de Datos Hidrometeorológicos", 0)
                doc.add_paragraph(str(df.describe()))
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                return buffer

            word_buffer = export_word(df)
            st.download_button("📥 Descargar Word", word_buffer, file_name="informe.docx")

            # Función 6: Exportar a PDF
            st.subheader("🧾 Exportar Informe PDF")
            def export_pdf(df):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, f"Informe generado el {datetime.now()}\n\n")
                for i in range(min(20, len(df))):
                    row = ', '.join([str(x) for x in df.iloc[i]])
                    pdf.multi_cell(0, 10, row)
                pdf_output_path = "/tmp/informe.pdf"
                pdf.output(pdf_output_path)
                return pdf_output_path

            pdf_path = export_pdf(df)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Descargar PDF", f, file_name="informe.pdf")

            # Función 7-15: Placeholder para más funciones...
            for i in range(7, 16):
                st.subheader(f"⚙️ Función {i}: (En desarrollo)")
                st.info("Aquí se implementará una herramienta avanzada para administración.")

        else:
            st.info("Por favor, carga un archivo CSV para comenzar.")

    else:
        st.title("🔒 Acceso restringido")
        st.warning("Tu cuenta no tiene permisos de administrador.")
            
