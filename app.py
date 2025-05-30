import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Hidromet Pro", layout="wide")

st.title("🌧️ Sistema de Análisis Hidrometeorológico Avanzado")
st.markdown("---")

# Sidebar
st.sidebar.title("🔧 Herramientas")
st.sidebar.markdown("Sube un archivo de mediciones para iniciar el análisis.")
uploaded_file = st.sidebar.file_uploader("Subir archivo CSV", type=["csv"])

# Función para generar informe PDF
def generate_pdf(text, df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=text)

    pdf.ln(10)
    for i, row in df.iterrows():
        row_str = ', '.join([str(val) for val in row])
        pdf.cell(0, 10, txt=row_str, ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Función para generar informe Word
def generate_word(text, df):
    doc = Document()
    doc.add_heading('Informe Hidrometeorológico', 0)
    doc.add_paragraph(text)

    if not df.empty:
        doc.add_heading("Datos procesados", level=1)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, column in enumerate(df.columns):
            hdr_cells[i].text = column

        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, value in enumerate(row):
                row_cells[i].text = str(value)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Procesamiento de archivo subido
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Archivo cargado correctamente.")

        st.subheader("📊 Vista previa de los datos")
        st.dataframe(df)

        # Estadísticas básicas
        st.subheader("📈 Análisis estadístico")
        st.write(df.describe())

        # Visualización simple
        st.subheader("📉 Visualización")
        selected_column = st.selectbox("Selecciona una columna para graficar", df.columns)
        fig, ax = plt.subplots()
        df[selected_column].plot(kind='line', ax=ax)
        ax.set_title(f"Tendencia de {selected_column}")
        st.pyplot(fig)

        # Informe generado
        st.subheader("📝 Redacción del informe")
        informe_text = st.text_area("Escribe tu resumen o informe aquí", height=200)

        # Botones de exportación
        if st.button("📤 Exportar a PDF"):
            if informe_text:
                pdf_buffer = generate_pdf(informe_text, df)
                st.download_button(label="📄 Descargar PDF", data=pdf_buffer, file_name="informe.pdf", mime="application/pdf")
            else:
                st.warning("Por favor, escribe un informe antes de exportar.")

        if st.button("📄 Exportar a Word"):
            if informe_text:
                word_buffer = generate_word(informe_text, df)
                st.download_button(label="📘 Descargar Word", data=word_buffer, file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            else:
                st.warning("Por favor, escribe un informe antes de exportar.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")

else:
    st.info("Por favor, sube un archivo CSV para iniciar.")
