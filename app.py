import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import base64

# Estilo general
st.set_page_config(page_title="HidroClimaPRO", layout="wide")

# Encabezado
st.title("HidroClimaPRO - Plataforma de Análisis Hidrometeorológico")

# Carga de archivo
st.sidebar.header("1. Subir archivo")
uploaded_file = st.sidebar.file_uploader("Carga un archivo CSV", type=["csv"])

# Función para convertir a PDF
def generate_pdf(df, report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(40, 40, 40)

    pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
    pdf.ln(10)

    pdf.multi_cell(0, 10, report_text)
    pdf.ln(5)

    # Agregar tabla
    col_names = df.columns.tolist()
    col_width = pdf.w / (len(col_names) + 1)

    pdf.set_fill_color(220, 220, 220)
    for col in col_names:
        pdf.cell(col_width, 10, col, border=1, fill=True)
    pdf.ln()

    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Función para exportar a Word
def generate_docx(df, report_text):
    doc = Document()
    doc.add_heading("Informe Hidrometeorológico", 0)

    doc.add_paragraph(report_text)

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
    return buffer

# Procesamiento de archivo
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("Vista previa de los datos")
        st.dataframe(df, use_container_width=True)

        st.subheader("Análisis de Datos")
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Selecciona una columna numérica para analizar", numeric_cols)

            fig = px.line(df, y=selected_col, title=f"Gráfico de {selected_col}")
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("No se encontraron columnas numéricas para graficar.")

        # Generación de informe
        st.subheader("Generar informe")
        report_text = st.text_area("Escribe un resumen para el informe", height=150)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Exportar a PDF"):
                try:
                    pdf_buffer = generate_pdf(df, report_text)
                    st.download_button("Descargar PDF", pdf_buffer, file_name="informe_hidromet.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Error al generar PDF: {e}")

        with col2:
            if st.button("Exportar a Word"):
                try:
                    word_buffer = generate_docx(df, report_text)
                    st.download_button("Descargar Word", word_buffer, file_name="informe_hidromet.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                except Exception as e:
                    st.error(f"Error al generar Word: {e}")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
