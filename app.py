import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="HidroClimaPro", layout="wide")

st.markdown("<h1 style='text-align: center;'>HidroClimaPro: Plataforma de Gestión Hidrometeorológica</h1>", unsafe_allow_html=True)
st.markdown("---")

uploaded_file = st.file_uploader("📂 Cargar archivo de datos (CSV)", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Archivo cargado correctamente.")

        st.subheader("🔍 Vista previa de los datos")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("📈 Análisis interactivo")

        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        date_columns = df.select_dtypes(include='object').columns.tolist()

        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("📅 Eje X (fecha o categoría)", options=df.columns)
        with col2:
            y_axis = st.selectbox("📊 Eje Y (valor numérico)", options=numeric_columns)

        if x_axis and y_axis:
            try:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df[x_axis], y=df[y_axis],
                                         mode='lines+markers',
                                         name='Tendencia'))
                fig.update_layout(
                    title=f"Gráfico: {y_axis} en función de {x_axis}",
                    xaxis_title=x_axis,
                    yaxis_title=y_axis,
                    template="plotly_white",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error al generar el gráfico: {e}")

        st.markdown("---")
        st.subheader("📝 Generar informe")

        with st.form("informe_form"):
            titulo = st.text_input("Título del informe", "Informe Hidrometeorológico")
            resumen = st.text_area("Resumen del informe")
            generar = st.form_submit_button("Generar documento")

        if generar:
            try:
                # Guardar informe en Word
                doc = Document()
                doc.add_heading(titulo, 0)
                doc.add_paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                doc.add_paragraph("Resumen:")
                doc.add_paragraph(resumen)
                doc.add_paragraph("Datos:")
                table = doc.add_table(rows=1, cols=len(df.columns))
                hdr_cells = table.rows[0].cells
                for i, col_name in enumerate(df.columns):
                    hdr_cells[i].text = col_name
                for _, row in df.iterrows():
                    row_cells = table.add_row().cells
                    for i, value in enumerate(row):
                        row_cells[i].text = str(value)
                word_stream = BytesIO()
                doc.save(word_stream)
                word_stream.seek(0)
                st.download_button("⬇️ Descargar informe Word", word_stream,
                                   file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

                # Guardar informe en PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(200, 10, titulo, ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(200, 10, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
                pdf.multi_cell(0, 10, f"Resumen:\n{resumen}")
                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                col_width = pdf.w / (len(df.columns) + 1)
                for col in df.columns:
                    pdf.cell(col_width, 10, col, 1)
                pdf.ln()
                pdf.set_font("Arial", "", 10)
                for _, row in df.iterrows():
                    for item in row:
                        pdf.cell(col_width, 10, str(item), 1)
                    pdf.ln()
                pdf_stream = BytesIO()
                pdf.output(pdf_stream)
                pdf_stream.seek(0)
                st.download_button("⬇️ Descargar informe PDF", pdf_stream,
                                   file_name="informe.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"❌ Error al generar documentos: {e}")
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.warning("Por favor, sube un archivo CSV para comenzar.")
