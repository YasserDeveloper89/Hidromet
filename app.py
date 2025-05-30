import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="HidroClimaPRO", layout="wide")

# ==================== MODO OSCURO/CLARO ====================
theme = st.sidebar.radio("Selecciona tema:", ["Claro", "Oscuro"])
if theme == "Oscuro":
    st.markdown("""
        <style>
            body { background-color: #1e1e1e; color: #ffffff; }
            .stApp { background-color: #1e1e1e; color: #ffffff; }
            .css-18e3th9, .css-1d391kg { background-color: #1e1e1e; color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

# ==================== CARGA DE ARCHIVO ====================
st.title("📊 HidroClimaPRO - Sistema Integral de Reportes")
uploaded_file = st.file_uploader("Carga un archivo CSV o Excel", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success("Archivo cargado correctamente.")

        st.subheader("Vista previa de los datos")
        st.dataframe(df, use_container_width=True)

        # ==================== ANÁLISIS AVANZADO ====================
        st.subheader("🔬 Análisis de datos")
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime64", "object"]).columns.tolist()

        col_to_plot = st.selectbox("Selecciona una columna numérica para analizar", numeric_cols)
        if col_to_plot:
            st.write(f"Resumen estadístico de **{col_to_plot}**")
            st.write(df[col_to_plot].describe())
            fig, ax = plt.subplots()
            df[col_to_plot].hist(bins=30, edgecolor='black', ax=ax)
            ax.set_title(f"Histograma de {col_to_plot}")
            ax.set_xlabel(col_to_plot)
            ax.set_ylabel("Frecuencia")
            st.pyplot(fig)

        # ==================== VISUALIZACIÓN AVANZADA ====================
        st.subheader("📈 Visualización de datos")
        time_col = st.selectbox("Selecciona columna de fecha (opcional)", date_cols)
        metric_col = st.selectbox("Selecciona métrica a visualizar", numeric_cols)

        if time_col and metric_col:
            try:
                df[time_col] = pd.to_datetime(df[time_col])
                df_sorted = df.sort_values(by=time_col)
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(df_sorted[time_col], df_sorted[metric_col], marker="o")
                ax.set_title(f"{metric_col} a lo largo del tiempo")
                ax.set_xlabel("Fecha")
                ax.set_ylabel(metric_col)
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"Error en visualización: {e}")

        # ==================== GENERACIÓN DE INFORMES ====================
        st.subheader("📝 Generación de informe")
        titulo = st.text_input("Título del informe")
        resumen = st.text_area("Resumen o conclusiones")

        def generar_pdf(dataframe, titulo, resumen):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, titulo, ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 10, resumen)
            pdf.ln()

            pdf.set_font("Arial", "B", 10)
            col_width = pdf.w / (len(dataframe.columns) + 1)
            row_height = pdf.font_size * 1.5
            for col in dataframe.columns:
                pdf.cell(col_width, row_height, col, border=1)
            pdf.ln(row_height)
            pdf.set_font("Arial", "", 10)
            for _, row in dataframe.iterrows():
                for item in row:
                    pdf.cell(col_width, row_height, str(item), border=1)
                pdf.ln(row_height)

            output = BytesIO()
            pdf.output(output)
            return output.getvalue()

        def generar_word(dataframe, titulo, resumen):
            doc = Document()
            doc.add_heading(titulo, 0)
            doc.add_paragraph(resumen)
            doc.add_paragraph(" ")

            table = doc.add_table(rows=1, cols=len(dataframe.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(dataframe.columns):
                hdr_cells[i].text = str(col)

            for _, row in dataframe.iterrows():
                row_cells = table.add_row().cells
                for i, item in enumerate(row):
                    row_cells[i].text = str(item)

            output = BytesIO()
            doc.save(output)
            return output.getvalue()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Exportar a PDF"):
                try:
                    pdf_data = generar_pdf(df, titulo, resumen)
                    b64_pdf = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="informe.pdf">Descargar PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error al generar PDF: {e}")

        with col2:
            if st.button("📝 Exportar a Word"):
                try:
                    word_data = generar_word(df, titulo, resumen)
                    b64_word = base64.b64encode(word_data).decode()
                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="informe.docx">Descargar Word</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error al generar Word: {e}")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
