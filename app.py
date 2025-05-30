import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="HydroClimaPRO", layout="wide")

# Función para cargar datos de muestra
@st.cache_data
def cargar_datos_ejemplo():
    fechas = pd.date_range(start='2024-01-01', periods=30, freq='D')
    datos = {
        "Fecha": fechas,
        "Temperatura (°C)": np.random.uniform(15, 35, len(fechas)).round(1),
        "Precipitación (mm)": np.random.uniform(0, 20, len(fechas)).round(1),
        "Humedad (%)": np.random.uniform(40, 90, len(fechas)).round(1)
    }
    return pd.DataFrame(datos)

# Título principal
st.title("📊 HydroClimaPRO - Plataforma Inteligente de Datos Meteorológicos")

# Cargar archivo
st.sidebar.header("📂 Cargar Datos")
archivo_subido = st.sidebar.file_uploader("Carga un archivo CSV", type=["csv"])

# Mostrar datos
if archivo_subido is not None:
    df = pd.read_csv(archivo_subido, parse_dates=True)
else:
    df = cargar_datos_ejemplo()
    st.sidebar.info("Usando datos de ejemplo (simulados).")

st.subheader("📋 Vista Previa de Datos")
st.dataframe(df, use_container_width=True)

# Análisis rápido
st.subheader("📈 Análisis Rápido de Estadísticas")
st.write(df.describe().T.style.background_gradient(cmap='Blues').format("{:.2f}"))

# Visualización de datos
st.subheader("📉 Visualización Interactiva")
columna_seleccionada = st.selectbox("Selecciona una variable para graficar:", df.select_dtypes(include=np.number).columns)

if columna_seleccionada:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[columna_seleccionada],
                             mode='lines+markers',
                             line=dict(color='deepskyblue', width=2),
                             marker=dict(size=6),
                             name=columna_seleccionada))
    fig.update_layout(
        title=f"{columna_seleccionada} en el tiempo",
        xaxis_title="Índice o Fecha",
        yaxis_title=columna_seleccionada,
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# Generar informe
st.subheader("📝 Generar Informe")

titulo = st.text_input("Título del Informe", value="Informe Meteorológico Detallado")
resumen = st.text_area("Resumen o Conclusiones", height=150)

def generar_pdf(titulo, resumen, df):
    buffer = BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, titulo, ln=1)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, resumen)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    for col in df.columns:
        pdf.cell(40, 10, col, 1)
    pdf.ln()

    pdf.set_font("Arial", '', 10)
    for i in range(min(len(df), 20)):
        for col in df.columns:
            pdf.cell(40, 10, str(df[col].iloc[i]), 1)
        pdf.ln()

    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def generar_docx(titulo, resumen, df):
    buffer = BytesIO()
    doc = Document()
    doc.add_heading(titulo, 0)
    doc.add_paragraph(resumen)

    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col

    for i in range(min(len(df), 20)):
        row_cells = table.add_row().cells
        for j, col in enumerate(df.columns):
            row_cells[j].text = str(df[col].iloc[i])

    doc.save(buffer)
    buffer.seek(0)
    return buffer

col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Exportar como PDF"):
        try:
            pdf_buffer = generar_pdf(titulo, resumen, df)
            st.download_button("⬇️ Descargar PDF", pdf_buffer, file_name="informe_meteorologico.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

with col2:
    if st.button("📝 Exportar como Word"):
        try:
            word_buffer = generar_docx(titulo, resumen, df)
            st.download_button("⬇️ Descargar DOCX", word_buffer, file_name="informe_meteorologico.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.error(f"Error al generar Word: {e}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray;'>HydroClimaPRO v1.0 · Todos los derechos reservados · 2025</div>",
    unsafe_allow_html=True
  )
