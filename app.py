import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF
import os

# Configuración general
st.set_page_config(page_title="HidroClimaPro", layout="wide")

# Estilos modernos
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', sans-serif;
        }
        .reportview-container {
            padding: 1.5rem 2rem 2rem 2rem;
        }
        h1, h2, h3 {
            color: #003366;
        }
        .stButton>button {
            background-color: #004488;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
        .stFileUploader label {
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌎 HidroClimaPro - Plataforma de Reportes Hidrometeorológicos")
st.markdown("Aplicación avanzada para análisis, carga de datos y generación de reportes en PDF y Word sobre variables hidrológicas y meteorológicas.")

# --- SUBIDA DE ARCHIVO ---
st.header("📁 Carga de Datos")
archivo = st.file_uploader("Carga tu archivo de datos (.csv, .xlsx, .json):", type=["csv", "xlsx", "json"])

if archivo:
    nombre = archivo.name

    try:
        if nombre.endswith(".csv"):
            df = pd.read_csv(archivo)
        elif nombre.endswith(".xlsx"):
            df = pd.read_excel(archivo)
        elif nombre.endswith(".json"):
            df = pd.read_json(archivo)
        else:
            st.error("Formato no soportado.")
            st.stop()

        st.success("✅ Archivo cargado correctamente")
        st.subheader("📊 Vista previa de los datos")
        st.dataframe(df, use_container_width=True)

        # Variables disponibles
        columnas = df.columns.tolist()
        st.markdown("#### Selecciona columnas para el reporte:")
        seleccionadas = st.multiselect("Columnas:", columnas, default=columnas[:3])

        df_filtrado = df[seleccionadas]

        # --- EXPORTAR A PDF ---
        def generar_pdf(dataframe):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt="Reporte Hidroclimático", ln=1, align="C")
            pdf.ln(5)

            col_width = pdf.w / (len(dataframe.columns) + 1)
            for col in dataframe.columns:
                pdf.cell(col_width, 10, col, border=1)
            pdf.ln()

            for i, row in dataframe.iterrows():
                for item in row:
                    pdf.cell(col_width, 10, str(item), border=1)
                pdf.ln()

            output = BytesIO()
            pdf.output(output)
            return output.getvalue()

        # --- EXPORTAR A WORD ---
        def generar_word(dataframe):
            doc = Document()
            doc.add_heading("Reporte Hidroclimático", 0)
            t = doc.add_table(rows=1, cols=len(dataframe.columns))
            hdr_cells = t.rows[0].cells
            for i, col in enumerate(dataframe.columns):
                hdr_cells[i].text = col

            for _, row in dataframe.iterrows():
                row_cells = t.add_row().cells
                for i, val in enumerate(row):
                    row_cells[i].text = str(val)

            output = BytesIO()
            doc.save(output)
            return output.getvalue()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬇️ Descargar PDF"):
                pdf_bytes = generar_pdf(df_filtrado)
                b64_pdf = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="reporte_hidroclimatico.pdf">📄 Descargar Reporte PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

        with col2:
            if st.button("⬇️ Descargar Word"):
                word_bytes = generar_word(df_filtrado)
                b64_doc = base64.b64encode(word_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64_doc}" download="reporte_hidroclimatico.docx">📝 Descargar Reporte Word</a>'
                st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Esperando un archivo de entrada para comenzar...")
