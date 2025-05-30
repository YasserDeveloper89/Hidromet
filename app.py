import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np

# Configuración inicial
st.set_page_config(page_title="HidroClimaPro", layout="wide")

# Estilo de la app (modo claro/oscuro)
modo = st.sidebar.radio("Modo de visualización", ["Claro", "Oscuro"])
if modo == "Oscuro":
    st.markdown("""
        <style>
        body { background-color: #1e1e1e; color: white; }
        </style>
    """, unsafe_allow_html=True)

# Cargar archivo
st.title("🔍 Plataforma de Análisis Hidrometeorológico")
archivo = st.file_uploader("Cargar archivo de mediciones (CSV)", type=["csv"])

if archivo is not None:
    try:
        df = pd.read_csv(archivo)
        st.subheader("Vista previa del archivo cargado:")
        st.dataframe(df)

        # Análisis básico
        st.subheader("📊 Análisis de Datos")
        st.write("Columnas disponibles:", df.columns.tolist())

        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_cols:
            col_select = st.selectbox("Seleccionar columna numérica para visualizar", numeric_cols)
            if col_select:
                st.line_chart(df[col_select])
        else:
            st.warning("No se encontraron columnas numéricas para graficar.")

        # Generar informe personalizado
        st.subheader("📝 Generar Informe")
        resumen = st.text_area("Escribe el resumen del informe")

        # Exportar a PDF
        if st.button("📥 Exportar Informe a PDF"):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
                pdf.ln(10)
                pdf.multi_cell(0, 10, resumen)
                pdf.ln(10)

                # Insertar tabla
                for col in df.columns:
                    pdf.cell(40, 10, col, border=1)
                pdf.ln()
                for i in range(min(len(df), 10)):
                    for col in df.columns:
                        pdf.cell(40, 10, str(df.iloc[i][col]), border=1)
                    pdf.ln()

                pdf_output = BytesIO()
                pdf.output(pdf_output)
                pdf_output.seek(0)
                st.download_button("Descargar PDF", data=pdf_output, file_name="informe.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")

        # Exportar a Word
        if st.button("📝 Exportar Informe a Word"):
            try:
                doc = Document()
                doc.add_heading('Informe Hidrometeorológico', 0)
                doc.add_paragraph(resumen)

                table = doc.add_table(rows=1, cols=len(df.columns))
                hdr_cells = table.rows[0].cells
                for i, col in enumerate(df.columns):
                    hdr_cells[i].text = str(col)
                for i in range(min(len(df), 10)):
                    row_cells = table.add_row().cells
                    for j, col in enumerate(df.columns):
                        row_cells[j].text = str(df.iloc[i][col])

                word_output = BytesIO()
                doc.save(word_output)
                word_output.seek(0)
                st.download_button("Descargar Word", data=word_output, file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")

    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
else:
    st.info("Por favor, carga un archivo CSV para comenzar.")
