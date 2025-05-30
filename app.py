import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document

st.set_page_config(page_title="HidroClimaPro", layout="wide")

# Estilo moderno
st.markdown("""
    <style>
    .main {background-color: #f4f6f8;}
    .block-container {
        padding: 2rem 2rem 1rem 2rem;
    }
    .stButton>button {
        color: white;
        background-color: #006699;
        border-radius: 8px;
        padding: 10px 16px;
    }
    h1, h2, h3, h4 {
        color: #003366;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.title("🌧️ HidroClimaPro - Análisis de Datos Hidrometeorológicos")
st.markdown("Importa, analiza y genera informes técnicos en segundos.")

# Cargar archivo
st.sidebar.header("📂 Cargar archivo de datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo .csv con tus datos", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Vista previa de datos")
    st.dataframe(df.head(), use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Estadísticas generales")
    st.write(df.describe())

    # Generar informe PDF
    st.subheader("📄 Generar informe")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Descargar informe en PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
            pdf.ln(10)

            for i, row in df.iterrows():
                texto = f"{row[0]}: "
                for col in df.columns[1:]:
                    texto += f"{col}={row[col]}  "
                pdf.multi_cell(0, 10, txt=texto)
                if i > 20:
                    break

            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)
            b64_pdf = base64.b64encode(pdf_output.read()).decode()
            href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="informe_hidrometeorologico.pdf">📥 Descargar PDF</a>'
            st.markdown(href_pdf, unsafe_allow_html=True)

    with col2:
        # Generar informe Word
        doc = Document()
        doc.add_heading('Resumen de datos hidrometeorológicos', level=1)

        for i, row in df.iterrows():
            texto = f"{row[0]}: "
            for col in df.columns[1:]:
                texto += f"{col}={row[col]}  "
            doc.add_paragraph(texto)
            if i > 20:
                break

        word_output = BytesIO()
        doc.save(word_output)
        word_output.seek(0)
        b64_word = base64.b64encode(word_output.read()).decode()
        href_word = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="informe_hidrometeorologico.docx">📥 Descargar Word</a>'
        st.markdown(href_word, unsafe_allow_html=True)

else:
    st.info("Por favor, sube un archivo .csv desde el menú lateral para comenzar.")
