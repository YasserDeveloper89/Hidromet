import streamlit as st import pandas as pd import numpy as np import base64 from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt import plotly.graph_objects as go from datetime import datetime

Función para generar PDF

def generate_pdf(df, summary, chart_img): pdf = FPDF() pdf.add_page() pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align='C')
pdf.ln(10)
pdf.multi_cell(0, 10, txt=f"Resumen del informe:\n{summary}\n")
pdf.ln(5)

# Guardar imagen temporalmente para insertar
img_path = "chart_temp.png"
with open(img_path, "wb") as f:
    f.write(chart_img.getbuffer())
pdf.image(img_path, x=10, w=180)
pdf.ln(5)

pdf.cell(200, 10, txt="Tabla de datos:", ln=True)
for i, row in df.iterrows():
    row_str = ", ".join(str(val) for val in row)
    pdf.multi_cell(0, 10, txt=row_str)

output = BytesIO()
pdf.output(output)
output.seek(0)
return output

Función para generar Word

def generate_word(df, summary): doc = Document() doc.add_heading("Informe Hidrometeorológico", 0) doc.add_paragraph(summary) doc.add_heading("Tabla de datos:", level=1)

table = doc.add_table(rows=1, cols=len(df.columns))
hdr_cells = table.rows[0].cells
for i, col in enumerate(df.columns):
    hdr_cells[i].text = col
for _, row in df.iterrows():
    row_cells = table.add_row().cells
    for i, val in enumerate(row):
        row_cells[i].text = str(val)

output = BytesIO()
doc.save(output)
output.seek(0)
return output

Función para generar gráfico con Plotly

def create_plot(df): fig = go.Figure() numeric_cols = df.select_dtypes(include=np.number).columns for col in numeric_cols: fig.add_trace(go.Scatter(x=df[df.columns[0]], y=df[col], mode='lines+markers', name=col)) fig.update_layout(title='Visualización de Datos', xaxis_title='Fecha', yaxis_title='Valores') return fig

Interfaz Streamlit

st.set_page_config(layout="wide") st.title("Plataforma Hidrometeorológica Corporativa")

Subida de archivo

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"]) if uploaded_file is not None: df = pd.read_csv(uploaded_file)

st.subheader("Vista Previa de los Datos")
st.dataframe(df, use_container_width=True)

# Resumen automático
st.subheader("Resumen de Datos")
summary = df.describe().to_string()
st.text(summary)

# Visualización
st.subheader("Visualización de Datos")
try:
    fig = create_plot(df)
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error("Error generando gráficos: " + str(e))

# Exportar informe
st.subheader("Generar Informe")
informe_text = st.text_area("Escribe un resumen del informe")

if st.button("Generar Documento"):
    chart_buf = BytesIO()
    fig.write_image(chart_buf, format="png")
    chart_buf.seek(0)

    pdf_file = generate_pdf(df, informe_text, chart_buf)
    st.download_button("Descargar Informe PDF", data=pdf_file, file_name="informe.pdf", mime="application/pdf")

    word_file = generate_word(df, informe_text)
    st.download_button("Descargar Informe Word", data=word_file, file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# Extra: análisis correlacional
st.subheader("Análisis Correlacional")
if len(df.select_dtypes(include=np.number).columns) >= 2:
    st.dataframe(df.corr(), use_container_width=True)

else: st.info("Por favor, sube un archivo CSV para comenzar.")

