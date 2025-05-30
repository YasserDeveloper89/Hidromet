import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="HidroClimaPRO", layout="wide")

# ---- INTERFAZ ----
st.title("🌦️ HidroClimaPRO - Plataforma de Monitoreo y Reportes")
st.markdown("Versión corporativa para gestión de datos hidrológicos y climáticos")

st.sidebar.header("🔍 Cargar archivo de datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])

df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Visualización avanzada de datos")

    selected_column = st.selectbox("Selecciona una columna numérica para graficar:", df.select_dtypes(include=np.number).columns)

    if selected_column:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[selected_column], mode='lines+markers', name=selected_column))
        fig.update_layout(title=f"Gráfico de {selected_column}", xaxis_title="Índice", yaxis_title=selected_column)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Análisis estadístico")
    st.write(df.describe())

    st.markdown("---")
    st.subheader("📝 Generar informe")

    informe_texto = st.text_area("Escribe un resumen del informe que acompañará los datos", height=200)

    def generar_pdf(dataframe, resumen):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe HidroClimaPRO", ln=True, align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, resumen)
        pdf.ln(5)
        col_names = dataframe.columns.tolist()
        pdf.set_font("Arial", size=10)

        for index, row in dataframe.iterrows():
            row_data = ', '.join([f"{col}: {row[col]}" for col in col_names])
            pdf.multi_cell(0, 10, row_data)
            if index > 20:
                break  # Para evitar PDF extremadamente largos en demo

        pdf_output = BytesIO()
        pdf.output(pdf_output, 'F')
        pdf_output.seek(0)
        return pdf_output

    def generar_word(dataframe, resumen):
        doc = Document()
        doc.add_heading("Informe HidroClimaPRO", 0)
        doc.add_paragraph(resumen)
        doc.add_paragraph("\nDatos principales:")
        table = doc.add_table(rows=1, cols=len(dataframe.columns))
        hdr_cells = table.rows[0].cells
        for i, col_name in enumerate(dataframe.columns):
            hdr_cells[i].text = str(col_name)
        for _, row in dataframe.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)
            if _ > 20:
                break

        word_output = BytesIO()
        doc.save(word_output)
        word_output.seek(0)
        return word_output

    if st.button("📄 Generar Documento PDF"):
        try:
            pdf_data = generar_pdf(df, informe_texto)
            st.download_button("📥 Descargar PDF", pdf_data, file_name="informe_hidroclima.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

    if st.button("📝 Generar Documento Word"):
        try:
            word_data = generar_word(df, informe_texto)
            st.download_button("📥 Descargar Word", word_data, file_name="informe_hidroclima.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.error(f"Error al generar Word: {e}")
