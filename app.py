import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF

st.set_page_config(page_title="HidroClima Pro", layout="wide")

st.title("🌧️ HidroClima Pro")
st.markdown("Sistema profesional para análisis de datos hidrometeorológicos.")

archivo = st.file_uploader("📁 Cargar archivo CSV o Excel", type=["csv", "xlsx"])

if archivo:
    try:
        df = pd.read_csv(archivo) if archivo.name.endswith(".csv") else pd.read_excel(archivo)
        st.success("✅ Archivo cargado exitosamente.")
        st.dataframe(df)

        st.subheader("📝 Generar informe")
        resumen = st.text_area("Escribe tu informe aquí:", height=200)

        if resumen.strip():
            # Word
            word_output = BytesIO()
            doc = Document()
            doc.add_heading("Informe HidroClima", level=1)
            doc.add_paragraph(resumen)
            doc.save(word_output)
            word_output.seek(0)

            # PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for linea in resumen.split('\n'):
                pdf.multi_cell(0, 10, linea)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            pdf_output = BytesIO(pdf_bytes)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📄 Descargar Word", word_output,
                                   file_name="informe_hidroclima.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            with col2:
                st.download_button("📄 Descargar PDF", pdf_output,
                                   file_name="informe_hidroclima.pdf",
                                   mime="application/pdf")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("📂 Carga un archivo para comenzar.")
