import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF
import base64

st.set_page_config(page_title="HidroClimaPro", layout="wide")

st.title("🌧️ HidroClimaPro - Análisis de Datos Hidrometeorológicos")

st.markdown("#### 📂 Subir archivo de datos (CSV, XLSX, JSON)")
archivo = st.file_uploader("Selecciona un archivo", type=["csv", "xlsx", "json"])

if archivo:
    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo)
        elif archivo.name.endswith(".xlsx"):
            df = pd.read_excel(archivo)
        elif archivo.name.endswith(".json"):
            df = pd.read_json(archivo)
        else:
            st.error("Formato no soportado.")
            st.stop()

        st.subheader("✅ Vista previa de los datos")
        st.dataframe(df)

        st.subheader("📊 Análisis básico")
        st.write(df.describe())

        # Función para exportar a PDF (de manera correcta)
        def exportar_pdf(dataframe):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)

            pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=True, align="C")
            pdf.ln(10)

            for col in dataframe.columns:
                pdf.cell(40, 8, col[:15], 1, 0, 'C')
            pdf.ln()

            for _, row in dataframe.iterrows():
                for val in row:
                    pdf.cell(40, 8, str(val)[:15], 1, 0, 'C')
                pdf.ln()

            output = BytesIO()
            pdf.output(dest='F', name='informe_hidromet.pdf')  # Escribe como archivo físico
            with open('informe_hidromet.pdf', 'rb') as f:
                return f.read()

        # Función para exportar a Word
        def exportar_word(dataframe):
            doc = Document()
            doc.add_heading("Informe de Datos Hidrometeorológicos", 0)

            table = doc.add_table(rows=1, cols=len(dataframe.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(dataframe.columns):
                hdr_cells[i].text = str(col)

            for _, row in dataframe.iterrows():
                row_cells = table.add_row().cells
                for i, val in enumerate(row):
                    row_cells[i].text = str(val)

            output = BytesIO()
            doc.save(output)
            return output.getvalue()

        col1, col2 = st.columns(2)

        with col1:
            try:
                pdf_bytes = exportar_pdf(df)
                b64_pdf = base64.b64encode(pdf_bytes).decode()
                href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="informe_hidromet.pdf">📥 Descargar PDF</a>'
                st.markdown(href_pdf, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al generar el PDF: {e}")

        with col2:
            try:
                word_bytes = exportar_word(df)
                b64_word = base64.b64encode(word_bytes).decode()
                href_word = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="informe_hidromet.docx">📥 Descargar Word</a>'
                st.markdown(href_word, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al generar el Word: {e}")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
