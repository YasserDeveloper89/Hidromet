import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF
import base64

# Configuración inicial
st.set_page_config(page_title="HidroClima Pro", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
        padding: 2rem;
    }
    .report-box {
        border: 1px solid #d1d5db;
        border-radius: 10px;
        padding: 20px;
        background-color: #ffffff;
    }
    .btn-container {
        display: flex;
        gap: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar con roles
st.sidebar.title("👤 Tipo de usuario")
user_role = st.sidebar.selectbox("Selecciona tu rol:", ["Supervisor", "Técnico", "Invitado"])

st.sidebar.markdown("---")
st.sidebar.info("Funciones disponibles varían según el rol seleccionado.")

# Título principal
st.title("🌧️ HidroClima Pro")
st.markdown("Sistema avanzado para gestión y análisis de datos hidrometeorológicos.")

# Subida de archivos
st.subheader("📁 Cargar archivo de datos")
archivo = st.file_uploader("Importar archivo CSV o Excel", type=["csv", "xlsx"])

if archivo:
    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)

        st.success("✅ Archivo cargado exitosamente.")
        st.dataframe(df, use_container_width=True)

        # Análisis básico
        st.subheader("📊 Análisis de datos")
        columnas_numericas = df.select_dtypes(include=['float', 'int']).columns.tolist()

        if columnas_numericas:
            col = st.selectbox("Selecciona una columna para analizar:", columnas_numericas)
            st.metric("Media", f"{df[col].mean():.2f}")
            st.metric("Máximo", f"{df[col].max():.2f}")
            st.metric("Mínimo", f"{df[col].min():.2f}")

        st.markdown("---")

        # Informe automático
        st.subheader("📝 Generar informe")
        resumen = st.text_area("Resumen personalizado del análisis", height=200)

        # Botones de descarga
        if resumen:
            # WORD
            doc = Document()
            doc.add_heading("Informe HidroClima", 0)
            doc.add_paragraph(resumen)
            word_output = BytesIO()
            doc.save(word_output)
            word_output.seek(0)

            # PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for linea in resumen.split("\n"):
                pdf.multi_cell(0, 10, linea)
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📄 Descargar Word", word_output,
                                   file_name="informe_hidroclima.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            with col2:
                st.download_button("📄 Descargar PDF", pdf_output,
                                   file_name="informe_hidroclima.pdf",
                                   mime="application/pdf")

        # Funciones avanzadas para Supervisor
        if user_role == "Supervisor":
            st.markdown("### ⚙️ Herramientas avanzadas")
            if st.button("📈 Generar reporte completo"):
                st.success("Reporte completo generado. (Funcionalidad demo)")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, carga un archivo para comenzar.")

# Footer profesional
st.markdown("""---""")
st.markdown("""
    <div style='text-align:center; color: gray; font-size: 14px;'>
        HidroClima Pro © 2025 - Desarrollado para operaciones hidrometeorológicas profesionales
    </div>
""", unsafe_allow_html=True)
