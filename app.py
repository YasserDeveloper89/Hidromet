import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np

# --- Configuración de página ---
st.set_page_config(page_title="HidroClimaPro", layout="wide")

# --- Selector de modo ---
modo = st.sidebar.selectbox("🎨 Modo de visualización", ["Claro", "Oscuro"])
estilo_tabla = "color: white; background-color: #333;" if modo == "Oscuro" else "color: black; background-color: white;"
estilo_titulo = "color: white;" if modo == "Oscuro" else "color: black;"

st.markdown(f"<h1 style='{estilo_titulo}'>🧪 Plataforma de Análisis Hidrometeorológico</h1>", unsafe_allow_html=True)

# --- Carga de archivo ---
archivo = st.file_uploader("📤 Cargar archivo de mediciones (CSV)", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo)

        # Vista previa
        st.markdown("### 🧾 Vista previa del archivo")
        st.dataframe(df.style.set_table_styles([{'selector': '', 'props': estilo_tabla}]))

        # Columnas
        st.markdown("### 🧠 Columnas disponibles para análisis:")
        for i, col in enumerate(df.columns):
            st.markdown(f"- **{i+1}. {col}**")

        # Visualización
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_cols:
            st.markdown("### 📈 Visualización de columna")
            col_select = st.selectbox("Selecciona una columna numérica", numeric_cols)
            st.line_chart(df[col_select])
        else:
            st.warning("No hay columnas numéricas para graficar.")

        # Generar informe
        st.markdown("### 📝 Generar Informe Resumido")
        resumen = st.text_area("Escribe un resumen o análisis:", height=200)

        # Exportar PDF
        def generar_pdf(dataframe, texto):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
            pdf.ln(10)
            pdf.multi_cell(0, 10, texto)
            pdf.ln(5)
            for col in dataframe.columns:
                pdf.cell(40, 10, col, border=1)
            pdf.ln()
            for i in range(min(len(dataframe), 10)):
                for col in dataframe.columns:
                    pdf.cell(40, 10, str(dataframe.iloc[i][col]), border=1)
                pdf.ln()
            return pdf.output(dest='S').encode('latin-1')

        # Exportar Word
        def generar_word(dataframe, texto):
            doc = Document()
            doc.add_heading('Informe Hidrometeorológico', 0)
            doc.add_paragraph(texto)
            table = doc.add_table(rows=1, cols=len(dataframe.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(dataframe.columns):
                hdr_cells[i].text = str(col)
            for i in range(min(len(dataframe), 10)):
                row_cells = table.add_row().cells
                for j, col in enumerate(dataframe.columns):
                    row_cells[j].text = str(dataframe.iloc[i][col])
            output = BytesIO()
            doc.save(output)
            return output

        st.markdown("### 📤 Exportar Informe")
        col1, col2 = st.columns(2)

        with col1:
            pdf_bytes = generar_pdf(df, resumen)
            st.download_button("📄 Descargar PDF", data=pdf_bytes, file_name="informe.pdf", mime="application/pdf")

        with col2:
            word_bytes = generar_word(df, resumen)
            word_bytes.seek(0)
            st.download_button("📝 Descargar Word", data=word_bytes, file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("Sube un archivo CSV para iniciar.")
