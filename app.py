import streamlit as st import pandas as pd import numpy as np from io import BytesIO from docx import Document from fpdf import FPDF import plotly.graph_objects as go from datetime import datetime

Configurar la página

st.set_page_config(page_title="HydroClimaPRO", layout="wide")

Estilo personalizado

st.markdown(""" <style> .reportview-container { background: #f9f9f9; color: #333333; } .main .block-container { padding-top: 2rem; padding-bottom: 2rem; padding-left: 3rem; padding-right: 3rem; } .stButton>button { border-radius: 12px; background-color: #0066cc; color: white; font-size: 16px; padding: 10px 24px; } </style> """, unsafe_allow_html=True)

Título de la app

st.title("HydroClimaPRO") st.subheader("Análisis de Datos Hidrometeorológicos Avanzado")

Cargar datos desde archivo de ejemplo o subir uno propio

with st.sidebar: st.header("Cargar Datos") uploaded_file = st.file_uploader("Carga tu archivo CSV", type=["csv"]) if uploaded_file is None: st.info("Cargando archivo de ejemplo...") uploaded_file = BytesIO(pd.DataFrame({ "Fecha": pd.date_range("2024-01-01", periods=10), "Temperatura (°C)": np.random.uniform(10, 30, 10), "Precipitación (mm)": np.random.uniform(0, 100, 10), "Humedad (%)": np.random.uniform(30, 90, 10) }).to_csv(index=False).encode())

Leer el archivo CSV

try: df = pd.read_csv(uploaded_file, parse_dates=["Fecha"]) st.success("Datos cargados correctamente.")

# Vista previa
st.subheader("Vista Previa de los Datos")
st.dataframe(df.head(10), use_container_width=True)

# Análisis estadístico
st.subheader("Resumen Estadístico")
st.dataframe(df.describe(), use_container_width=True)

# Visualización interactiva
st.subheader("Visualización de Datos")
columna = st.selectbox("Selecciona columna para graficar", df.select_dtypes(include=[np.number]).columns)
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Fecha"], y=df[columna], mode='lines+markers', name=columna))
fig.update_layout(title=f"Tendencia de {columna}", xaxis_title="Fecha", yaxis_title=columna,
                  template="plotly_dark", height=400)
st.plotly_chart(fig, use_container_width=True)

# Generar informe
st.subheader("Generar Informe")
resumen = st.text_area("Introduce un resumen para el informe:", height=150)

if st.button("Generar Documento"):
    # WORD
    doc = Document()
    doc.add_heading("Informe Hidrometeorológico", 0)
    doc.add_paragraph(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if resumen:
        doc.add_paragraph("Resumen del Informe:")
        doc.add_paragraph(resumen)
    doc.add_paragraph("\nDatos:")
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    st.download_button("Descargar Informe Word", buffer, file_name="informe_hidro.docx")

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    if resumen:
        pdf.multi_cell(0, 10, txt=f"\nResumen:\n{resumen}")
    pdf.ln(5)
    pdf.cell(0, 10, txt="\nDatos:", ln=True)
    for index, row in df.iterrows():
        line = ', '.join([f"{col}: {row[col]}" for col in df.columns])
        pdf.multi_cell(0, 10, txt=line)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    st.download_button("Descargar Informe PDF", pdf_output, file_name="informe_hidro.pdf")

except Exception as e: st.error(f"Error al procesar los datos: {e}")

