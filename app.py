import streamlit as st import pandas as pd import base64 from io import BytesIO from docx import Document from fpdf import FPDF

st.set_page_config(page_title="HydroClimaPro", layout="wide")

============================

Estilos personalizados

============================

st.markdown(""" <style> .block-container { padding-top: 2rem; padding-bottom: 1rem; font-family: 'Segoe UI', sans-serif; color: #222; } h1, h2, h3, h4 { color: #0A3D62; } .stButton>button { background-color: #0A3D62; color: white; border-radius: 0.5rem; padding: 0.5rem 1rem; font-size: 1rem; } .stFileUploader label { font-weight: bold; } .report-section { background: #f4f6f8; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; } </style> """, unsafe_allow_html=True)

============================

Encabezado

============================

st.title("🌧️ HydroClimaPro - Plataforma Avanzada de Reportes Hidrometeorológicos") st.markdown(""" Facilita la generación de reportes técnicos con importación, análisis y exportación de datos en formatos PDF y Word. """)

============================

Carga de datos

============================

st.subheader("📂 Importar archivos de medición") tab1, tab2 = st.tabs(["Excel / CSV", "Formato JSON"])

data = None with tab1: uploaded_file = st.file_uploader("Sube tu archivo Excel o CSV", type=["csv", "xlsx"]) if uploaded_file: if uploaded_file.name.endswith(".csv"): data = pd.read_csv(uploaded_file) else: data = pd.read_excel(uploaded_file)

with tab2: uploaded_json = st.file_uploader("Sube tu archivo JSON de sensores", type=["json"]) if uploaded_json: data = pd.read_json(uploaded_json)

if data is not None: st.success("Archivo cargado correctamente ✅") st.dataframe(data, use_container_width=True, height=400)

# ============================
# Análisis básico
# ============================
st.subheader("📊 Análisis inicial de datos")
st.markdown("""
A continuación se muestra una descripción general de los datos cargados.
""")
st.dataframe(data.describe(), use_container_width=True)

# ============================
# Exportación a PDF y Word
# ============================
st.subheader("📄 Generar informes automáticos")
report_title = st.text_input("Título del informe", "Informe Hidrometeorológico")

if st.button("📤 Exportar informe en Word y PDF"):

    # === WORD ===
    doc = Document()
    doc.add_heading(report_title, 0)
    doc.add_paragraph("Descripción estadística de los datos cargados:")
    desc_table = data.describe().reset_index()

    table = doc.add_table(rows=1, cols=len(desc_table.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(desc_table.columns):
        hdr_cells[i].text = col
    for _, row in desc_table.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)

    word_stream = BytesIO()
    doc.save(word_stream)
    word_stream.seek(0)

    # === PDF ===
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=report_title, align='C')
    pdf.ln()
    pdf.multi_cell(0, 10, txt="Resumen estadístico:")

    stats = data.describe().round(2)
    for col in stats.columns:
        pdf.cell(0, 10, f"{col}: {stats[col].to_dict()}", ln=1)

    pdf_stream = BytesIO()
    pdf.output(pdf_stream)
    pdf_stream.seek(0)

    # === Descargas ===
    st.download_button("📥 Descargar Word", word_stream, file_name="informe.docx")
    st.download_button("📥 Descargar PDF", pdf_stream, file_name="informe.pdf")

else: st.info("Por favor, carga un archivo para comenzar con el análisis y generación de reportes.")

