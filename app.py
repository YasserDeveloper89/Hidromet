import streamlit as st import pandas as pd import numpy as np import base64 from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt from datetime import datetime

--- Configuración inicial ---

st.set_page_config(page_title="Hidromet PRO", layout="wide") st.title("Hidromet PRO - Análisis Hidrometeorológico")

--- Modo claro/oscuro ---

theme_mode = st.sidebar.radio("Modo de visualización:", ("Claro", "Oscuro")) if theme_mode == "Oscuro": st.markdown(""" <style> .main {background-color: #1e1e1e; color: #e0e0e0;} .stTextInput > div > div > input {color: #e0e0e0; background-color: #333;} </style> """, unsafe_allow_html=True)

--- Subida de archivo ---

st.sidebar.header("Cargar archivo de datos") file = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])

--- Funciones auxiliares ---

def generar_pdf(dataframe, resumen): pdf = FPDF() pdf.add_page() pdf.set_font("Arial", size=12) pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C") pdf.ln(10) pdf.multi_cell(0, 10, resumen) pdf.ln(10) for col in dataframe.columns: pdf.cell(40, 10, col, border=1) pdf.ln() for i, row in dataframe.iterrows(): for val in row: pdf.cell(40, 10, str(val), border=1) pdf.ln() output = BytesIO() pdf.output(output) return output.getvalue()

def generar_word(dataframe, resumen): doc = Document() doc.add_heading("Informe Hidrometeorológico", 0) doc.add_paragraph(resumen) table = doc.add_table(rows=1, cols=len(dataframe.columns)) hdr_cells = table.rows[0].cells for i, col in enumerate(dataframe.columns): hdr_cells[i].text = str(col) for _, row in dataframe.iterrows(): row_cells = table.add_row().cells for i, val in enumerate(row): row_cells[i].text = str(val) output = BytesIO() doc.save(output) return output.getvalue()

if file is not None: try: df = pd.read_csv(file) st.success("Archivo cargado exitosamente")

# Vista previa de datos
    st.subheader("Vista previa de los datos")
    st.dataframe(df.head())

    # Sección: Análisis de datos
    st.subheader("Análisis de Datos")
    columnas_numericas = df.select_dtypes(include=np.number).columns.tolist()

    if columnas_numericas:
        opcion_columna = st.selectbox("Selecciona una columna para visualizar:", columnas_numericas)
        fig, ax = plt.subplots()
        df[opcion_columna].hist(ax=ax, bins=20, color='#00bfff')
        st.pyplot(fig)
    else:
        st.warning("No hay columnas numéricas para graficar.")

    # Sección: Informe
    st.subheader("Generar Informe")
    texto = st.text_area("Redacta un resumen del informe:")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Exportar a PDF"):
            try:
                contenido_pdf = generar_pdf(df, texto)
                b64 = base64.b64encode(contenido_pdf).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe.pdf">Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")

    with col2:
        if st.button("Exportar a Word"):
            try:
                contenido_word = generar_word(df, texto)
                b64 = base64.b64encode(contenido_word).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe.docx">Descargar Word</a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al generar Word: {e}")

    # Sección: Estadísticas avanzadas
    st.subheader("Estadísticas Descriptivas")
    st.write(df.describe())

except Exception as e:
    st.error(f"Error procesando el archivo: {e}")

else: st.info("Por favor, carga un archivo CSV para comenzar.")

