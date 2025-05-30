import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF
import base64
import plotly.express as px

st.set_page_config(page_title="HidroClimaPro", layout="wide")

# ---- ESTILOS ----
st.markdown("""
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            padding: 2rem;
        }
        .stButton>button {
            background-color: #0078D4;
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #005a9e;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌦️ HidroClimaPro - Plataforma de Análisis Hidrometeorológico")
st.markdown("Sube tus mediciones climáticas o hidrológicas y genera informes rápidamente.")

uploaded_file = st.file_uploader("📂 Sube un archivo de datos (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")

    st.subheader("🔍 Vista previa de los datos")
    st.dataframe(df.head(50))

    st.subheader("📊 Análisis estadístico")
    st.write(df.describe())

    st.subheader("📈 Visualización interactiva")
    columnas_numericas = df.select_dtypes(include='number').columns.tolist()
    if len(columnas_numericas) >= 2:
        eje_x = st.selectbox("Selecciona el eje X", columnas_numericas)
        eje_y = st.selectbox("Selecciona el eje Y", columnas_numericas, index=1)
        fig = px.scatter(df, x=eje_x, y=eje_y, title="Relación entre variables")
        st.plotly_chart(fig, use_container_width=True)

    def generar_docx(dataframe):
        doc = Document()
        doc.add_heading("Informe de Datos Hidrometeorológicos", 0)
        doc.add_paragraph("Resumen estadístico:")
        desc = dataframe.describe().reset_index()
        table = doc.add_table(rows=1, cols=len(desc.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(desc.columns):
            hdr_cells[i].text = str(col)
        for _, row in desc.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    def generar_pdf(dataframe):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
        pdf.ln(10)
        stats = dataframe.describe()
        for col in stats.columns:
            pdf.cell(200, 10, txt=f"Variable: {col}", ln=True)
            for stat in stats.index:
                val = stats.loc[stat, col]
                pdf.cell(200, 10, txt=f"  {stat}: {val:.2f}", ln=True)
            pdf.ln(5)
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        return BytesIO(pdf_bytes)

    st.subheader("📥 Exportar informe")

    col1, col2 = st.columns(2)

    with col1:
        docx_buffer = generar_docx(df)
        st.download_button(
            label="📄 Descargar informe en Word",
            data=docx_buffer,
            file_name="informe.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    with col2:
        pdf_buffer = generar_pdf(df)
        st.download_button(
            label="🧾 Descargar informe en PDF",
            data=pdf_buffer,
            file_name="informe.pdf",
            mime="application/pdf"
                )
