import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np

# ------------------------ Configuración de estilo ------------------------
st.set_page_config(page_title="Hidromet Pro", layout="wide")

# ------------------------ Modo Claro / Oscuro ------------------------
theme_mode = st.sidebar.radio("🌗 Modo de visualización", ["Claro", "Oscuro"])
if theme_mode == "Oscuro":
    st.markdown(
        """
        <style>
            body {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        </style>
        """, unsafe_allow_html=True
    )

# ------------------------ Título y descripción ------------------------
st.title("🌦️ Hidromet Pro - Análisis y Gestión de Datos Climáticos")
st.markdown("Sistema profesional para importar, visualizar, analizar y exportar informes de datos meteorológicos e hidrológicos.")

# ------------------------ Carga de archivo ------------------------
uploaded_file = st.file_uploader("📂 Subir archivo CSV", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Archivo cargado correctamente.")
        st.dataframe(df)

        # ------------------------ Visualización de datos ------------------------
        st.subheader("📊 Visualización de Datos")
        column = st.selectbox("Selecciona columna para graficar", df.columns)
        if pd.api.types.is_numeric_dtype(df[column]):
            fig, ax = plt.subplots()
            ax.plot(df[column])
            ax.set_title(f"Evolución de {column}")
            ax.set_xlabel("Índice")
            ax.set_ylabel(column)
            st.pyplot(fig)
        else:
            st.warning("⚠️ La columna seleccionada no contiene datos numéricos.")

        # ------------------------ Análisis de datos ------------------------
        st.subheader("📈 Análisis Estadístico")
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        if numeric_columns:
            analysis_column = st.selectbox("Selecciona una columna numérica", numeric_columns)
            stats = df[analysis_column].describe()
            st.write(stats)
            fig_hist, ax_hist = plt.subplots()
            ax_hist.hist(df[analysis_column], bins=20, color='skyblue', edgecolor='black')
            ax_hist.set_title(f"Distribución de {analysis_column}")
            st.pyplot(fig_hist)
        else:
            st.info("No se encontraron columnas numéricas para análisis.")

        # ------------------------ Informe ------------------------
        st.subheader("📝 Generar Informe")
        resumen = st.text_area("Resumen o comentarios del informe")

        def generar_pdf(df, resumen):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Informe de Datos Hidrometeorológicos", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, resumen)
            pdf.ln()

            pdf.set_font("Arial", "B", 12)
            for column in df.columns:
                pdf.cell(40, 10, str(column), border=1)
            pdf.ln()

            pdf.set_font("Arial", size=10)
            for _, row in df.iterrows():
                for item in row:
                    pdf.cell(40, 10, str(item), border=1)
                pdf.ln()

            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            return pdf_buffer.getvalue()

        def generar_word(df, resumen):
            doc = Document()
            doc.add_heading("Informe de Datos Hidrometeorológicos", 0)
            doc.add_paragraph(resumen)

            table = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = str(col)

            for _, row in df.iterrows():
                row_cells = table.add_row().cells
                for i, item in enumerate(row):
                    row_cells[i].text = str(item)

            doc_buffer = BytesIO()
            doc.save(doc_buffer)
            return doc_buffer.getvalue()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Exportar a PDF"):
                try:
                    pdf_data = generar_pdf(df, resumen)
                    b64_pdf = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="informe.pdf">Haz clic para descargar el PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el PDF: {e}")

        with col2:
            if st.button("📝 Exportar a Word"):
                try:
                    word_data = generar_word(df, resumen)
                    b64_word = base64.b64encode(word_data).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64_word}" download="informe.docx">Haz clic para descargar el Word</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el Word: {e}")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("🔄 Esperando que subas un archivo CSV para comenzar.")
