import streamlit as st 
import pandas as pd 
import numpy as np 
from io 
import BytesIO from docx 
import Document from fpdf 
import FPDF 
import plotly.graph_objects as go from datetime 
import datetime

st.set_page_config(page_title="HidroClimaPRO", layout="wide")

st.title("🌧️ HidroClimaPRO - Análisis Avanzado Hidrometeorológico")

uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV con datos meteorológicos", type=["csv"])

if uploaded_file: try: df = pd.read_csv(uploaded_file) st.success("✅ Archivo cargado correctamente") except Exception as e: st.error(f"❌ Error al leer el archivo: {e}") st.stop()

st.markdown("## 🧪 Vista Previa de los Datos")
st.dataframe(df.head())

st.markdown("## 📊 Visualización Interactiva")
num_cols = df.select_dtypes(include=np.number).columns
selected_column = st.selectbox("Selecciona una columna numérica", num_cols)

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

st.markdown("## 📈 Estadísticas Descriptivas Avanzadas")
if not num_cols.empty:
    st.write(df[num_cols].describe())

    st.markdown("#### 🤷‍♂️ Estadísticas Personalizadas")
    st.write("Coeficiente de variación:")
    st.write((df[num_cols].std() / df[num_cols].mean()).round(2))

    st.write("Mediana:")
    st.write(df[num_cols].median())

    st.write("Moda:")
    st.write(df[num_cols].mode().iloc[0])

    st.write("Valores máximos:")
    st.write(df[num_cols].max())

    st.write("Valores mínimos:")
    st.write(df[num_cols].min())

st.markdown("## 📄 Generar Informe")
report_text = st.text_area("Resumen del informe", placeholder="Escribe un resumen técnico...")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def generar_word():
    doc = Document()
    doc.add_heading("Informe Hidrometeorológico", 0)
    doc.add_paragraph(f"Fecha de generación: {timestamp}")
    doc.add_heading("Resumen:", level=1)
    doc.add_paragraph(report_text if report_text else "Sin resumen disponible.")
    doc.add_heading("Estadísticas:", level=1)
    doc.add_paragraph(df.describe().to_string())
    word_file = BytesIO()
    doc.save(word_file)
    word_file.seek(0)
    return word_file

def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Informe Hidrometeorológico", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Fecha: {timestamp}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Resumen:\n{report_text if report_text else 'Sin resumen.'}")
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Estadísticas descriptivas:\n" + df.describe().to_string())
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

col1, col2 = st.columns(2)
with col1:
    word_file = generar_word()
    st.download_button(
        label="📄 Descargar Informe Word",
        data=word_file,
        file_name=f"Informe_{timestamp}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

with col2:
    try:
        pdf_file = generar_pdf()
        st.download_button(
            label="📄 Descargar Informe PDF",
            data=pdf_file,
            file_name=f"Informe_{timestamp}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

else: st.info("📂 Carga un archivo CSV para comenzar el análisis.")

