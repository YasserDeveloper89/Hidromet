import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.shared import Inches
from fpdf import FPDF
import matplotlib.pyplot as plt

st.set_page_config(page_title="HidroClima Pro", layout="wide")
st.title("🌧️ HidroClima Pro")
st.markdown("Sistema profesional para análisis de datos hidrometeorológicos.")

archivo = st.file_uploader("📁 Cargar archivo CSV o Excel", type=["csv", "xlsx"])

if archivo:
    try:
        df = pd.read_csv(archivo) if archivo.name.endswith(".csv") else pd.read_excel(archivo)
        st.success("✅ Archivo cargado exitosamente.")
        st.dataframe(df)

        # Filtros y estadísticas
        with st.expander("🔍 Herramientas de Análisis"):
            st.subheader("Estadísticas")
            st.write(df.describe())

            st.subheader("Seleccionar columnas para análisis")
            columnas = st.multiselect("Selecciona columnas numéricas:", df.select_dtypes(include='number').columns)

            if columnas:
                st.line_chart(df[columnas])

        # Generar informe
        st.subheader("📝 Generar informe")
        resumen = st.text_area("Escribe tu informe aquí:", height=200)

        if resumen.strip():
            # ----------- WORD -------------
            word_output = BytesIO()
            doc = Document()
            doc.add_heading("Informe HidroClima", level=1)
            doc.add_paragraph(resumen)
            doc.add_heading("Datos de medición:", level=2)

            table = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = str(col)

            max_rows = 30
            for i, row in df.iterrows():
                if i >= max_rows:
                    break
                row_cells = table.add_row().cells
                for j, cell in enumerate(row):
                    row_cells[j].text = str(cell)

            doc.add_paragraph(f"⚠️ Mostrando solo las primeras {max_rows} filas." if len(df) > max_rows else "")
            doc.save(word_output)
            word_output.seek(0)

            # ----------- PDF --------------
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Informe HidroClima", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, resumen)
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Datos de medición:", ln=True)
            pdf.set_font("Arial", size=9)

            col_width = pdf.w / (len(df.columns) + 1)
            row_height = 6

            for col in df.columns:
                pdf.cell(col_width, row_height, str(col), border=1)
            pdf.ln(row_height)

            for i, row in df.iterrows():
                if i >= max_rows:
                    pdf.cell(0, 10, f"... Mostrando solo primeras {max_rows} filas", ln=True)
                    break
                for item in row:
                    pdf.cell(col_width, row_height, str(item), border=1)
                pdf.ln(row_height)

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            pdf_output = BytesIO(pdf_bytes)

            # ----------- BOTONES ----------
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📄 Descargar Word", word_output,
                                   file_name="informe_hidroclima.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            with col2:
                st.download_button("📄 Descargar PDF", pdf_output,
                                   file_name="informe_hidroclima.pdf",
                                   mime="application/pdf")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("📂 Carga un archivo para comenzar.")
