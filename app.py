import streamlit as st import pandas as pd import numpy as np from io import BytesIO from docx import Document from fpdf import FPDF import plotly.graph_objects as go from datetime import datetime

st.set_page_config(page_title="HidroClimaPRO", layout="wide", initial_sidebar_state="expanded")

----- ESTILOS GLOBALES -----

with open("/app/style.css") if False else BytesIO(): st.markdown(""" <style> .main { background-color: #f4f6f9; } .block-container { padding-top: 2rem; padding-bottom: 2rem; } .stButton>button { background-color: #0052cc; color: white; font-weight: bold; border-radius: 0.5rem; padding: 0.5rem 1rem; } .stDownloadButton>button { background-color: #36b37e; color: white; font-weight: bold; border-radius: 0.5rem; padding: 0.5rem 1rem; } </style> """, unsafe_allow_html=True)

----- SIDEBAR -----

st.sidebar.image("https://img.icons8.com/ios-filled/100/hydro-power.png", width=80) st.sidebar.title("🚀 HidroClimaPRO") menu = st.sidebar.radio("Menú Principal", ["Carga de datos", "Visualización de datos", "Análisis avanzado", "Generar informe"])

----- FUNCIONES -----

def generar_pdf(dataframe, resumen): pdf = FPDF() pdf.add_page() pdf.set_font("Arial", size=12) pdf.cell(200, 10, txt="Informe HidroClimaPRO", ln=True, align='C') pdf.ln(10) pdf.multi_cell(0, 10, resumen) pdf.ln(5) col_names = dataframe.columns.tolist() pdf.set_font("Arial", size=10)

for index, row in dataframe.iterrows():
    row_data = ', '.join([f"{col}: {row[col]}" for col in col_names])
    pdf.multi_cell(0, 10, row_data)
    if index > 20:
        break

pdf_output = BytesIO()
pdf.output(pdf_output, 'F')
pdf_output.seek(0)
return pdf_output

def generar_word(dataframe, resumen): doc = Document() doc.add_heading("Informe HidroClimaPRO", 0) doc.add_paragraph(resumen) doc.add_paragraph("\nDatos principales:") table = doc.add_table(rows=1, cols=len(dataframe.columns)) hdr_cells = table.rows[0].cells for i, col_name in enumerate(dataframe.columns): hdr_cells[i].text = str(col_name) for _, row in dataframe.iterrows(): row_cells = table.add_row().cells for i, item in enumerate(row): row_cells[i].text = str(item) if _ > 20: break word_output = BytesIO() doc.save(word_output) word_output.seek(0) return word_output

----- CARGA DE DATOS -----

df = None if menu == "Carga de datos": st.title("📁 Carga de Datos") uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"]) if uploaded_file is not None: df = pd.read_csv(uploaded_file) st.success("✅ Archivo cargado correctamente") st.dataframe(df, use_container_width=True)

----- VISUALIZACIÓN -----

elif menu == "Visualización de datos": st.title("📊 Visualización de Datos") if df is not None: columna = st.selectbox("Selecciona una columna para graficar:", df.select_dtypes(include=np.number).columns) fig = go.Figure() fig.add_trace(go.Scatter(x=df.index, y=df[columna], mode='lines+markers')) fig.update_layout(title=f"Evolución de {columna}", xaxis_title="Índice", yaxis_title=columna) st.plotly_chart(fig, use_container_width=True) else: st.warning("Primero debes cargar un archivo.")

----- ANÁLISIS AVANZADO -----

elif menu == "Análisis avanzado": st.title("📈 Análisis Avanzado") if df is not None: st.subheader("Resumen estadístico") st.dataframe(df.describe(), use_container_width=True)

st.subheader("Correlación entre variables")
    corr = df.corr()
    fig_corr = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale='Viridis'))
    fig_corr.update_layout(title="Mapa de Correlación")
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.warning("Primero debes cargar un archivo.")

----- GENERAR INFORME -----

elif menu == "Generar informe": st.title("📝 Generar Informe") if df is not None: resumen = st.text_area("Resumen del informe", height=150)

if st.button("📄 Generar PDF"):
        try:
            pdf_data = generar_pdf(df, resumen)
            st.download_button("📥 Descargar PDF", pdf_data, file_name="informe_hidroclima.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

    if st.button("📝 Generar Word"):
        try:
            word_data = generar_word(df, resumen)
            st.download_button("📥 Descargar Word", word_data, file_name="informe_hidroclima.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.error(f"Error al generar Word: {e}")
else:
    st.warning("Primero debes cargar un archivo.")

