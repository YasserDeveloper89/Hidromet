import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="HidroClimaPRO", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
        body {
            background-color: #f5f7fa;
        }
        .css-1d391kg {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 15px;
        }
        .reportview-container .main .block-container{
            padding: 2rem 3rem 2rem 3rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌧️ HidroClimaPRO - Análisis Avanzado Hidrometeorológico")

# Subida de datos
st.sidebar.header("📂 Cargar archivo")
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV con datos meteorológicos", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Archivo cargado correctamente")
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
        st.stop()

    st.markdown("## 🧮 Vista Previa de los Datos")
    st.dataframe(df.head())

    # Selección de columna para visualización
    st.markdown("## 📊 Visualización Interactiva")
    selected_column = st.selectbox("Selecciona una columna numérica", df.select_dtypes(include=np.number).columns)

    if selected_column:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[selected_column],
            mode='lines+markers',
            name=selected_column,
            line=dict(color='royalblue', width=2),
            marker=dict(size=6)
        ))
        fig.update_layout(title=f"Gráfico de {selected_column}",
                          xaxis_title="Índice",
                          yaxis_title=selected_column,
                          template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 📈 Estadísticas Descriptivas")
    st.write(df.describe())

    st.markdown("---")

    # Generar informe
    st.markdown("## 📝 Generar Informe")
    report_text = st.text_area("Escribe un resumen para el informe", placeholder="Resumen técnico o conclusiones...")

    # Botón para generar documentos
    if st.button("📄 Generar Documentos"):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Word
        doc = Document()
        doc.add_heading("Informe Hidrometeorológico", 0)
        doc.add_paragraph(f"Fecha de generación: {timestamp}")
        doc.add_heading("Resumen:", level=1)
        doc.add_paragraph(report_text if report_text else "Sin resumen.")
        doc.add_heading("Datos Analizados:", level=1)
        doc.add_paragraph("Vista previa de los primeros registros:")
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)
        for _, row in df.head(10).iterrows():
            row_cells = table.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
        word_file = BytesIO()
        doc.save(word_file)
        word_file.seek(0)

        # PDF
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "Informe Hidrometeorológico", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.ln(10)
            pdf.cell(200, 10, f"Fecha: {timestamp}", ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, "Resumen:", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 10, report_text if report_text else "Sin resumen.")

            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, "Vista previa de los datos:", ln=True)
            pdf.set_font("Arial", "", 10)
            for i, row in df.head(10).iterrows():
                row_text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
                pdf.multi_cell(0, 10, row_text)

            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            st.download_button(
                label="📥 Descargar Informe PDF",
                data=pdf_output,
                file_name=f"Informe_{timestamp}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

        # Descargar Word
        st.download_button(
            label="📥 Descargar Informe Word",
            data=word_file,
            file_name=f"Informe_{timestamp}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

else:
    st.warning("📎 Por favor sube un archivo CSV para comenzar.")
