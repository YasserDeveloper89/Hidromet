import streamlit as st import pandas as pd import numpy as np import base64 from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt import plotly.graph_objects as go from datetime import datetime

-------------------- CONFIGURACIÓN DE LA APP --------------------

st.set_page_config( page_title="HidroClima Pro", layout="wide", initial_sidebar_state="expanded", )

st.title("💧 HidroClima PRO - Plataforma de Análisis Hidrometeorológico") st.markdown("""<hr style='margin:1rem 0'>""", unsafe_allow_html=True)

-------------------- CARGA DE DATOS --------------------

with st.sidebar: st.header("📁 Cargar archivo") file = st.file_uploader("Sube un archivo CSV", type=["csv"])

if file: df = pd.read_csv(file) st.success("✅ Archivo cargado correctamente") st.markdown("### Vista previa de los datos") st.dataframe(df.head(), use_container_width=True)

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

# -------------------- VISUALIZACIÓN AVANZADA --------------------
st.markdown("---")
st.subheader("📊 Visualización avanzada de datos")

if numeric_cols:
    selected_col = st.selectbox("Selecciona una columna numérica para visualizar", numeric_cols)

    chart_type = st.radio(
        "Tipo de gráfico",
        options=["Línea", "Barras", "Área", "Boxplot"],
        horizontal=True,
        index=0,
    )

    fig = go.Figure()

    if chart_type == "Línea":
        fig.add_trace(go.Scatter(y=df[selected_col], mode='lines+markers', name=selected_col, line=dict(color='royalblue')))
    elif chart_type == "Barras":
        fig.add_trace(go.Bar(y=df[selected_col], name=selected_col, marker_color='indianred'))
    elif chart_type == "Área":
        fig.add_trace(go.Scatter(y=df[selected_col], fill='tozeroy', name=selected_col, line=dict(color='lightseagreen')))
    elif chart_type == "Boxplot":
        fig.add_trace(go.Box(y=df[selected_col], name=selected_col, marker_color='darkorange'))

    fig.update_layout(
        title=f"Gráfico de {selected_col}",
        xaxis_title="Índice",
        yaxis_title=selected_col,
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📈 Resumen estadístico de la columna"):
        stats = df[selected_col].describe().round(2)
        st.write(stats)
else:
    st.warning("⚠️ No se encontraron columnas numéricas para visualizar.")

# -------------------- GENERACIÓN DE INFORMES --------------------
st.markdown("---")
st.subheader("📝 Generar informe personalizado")
user_notes = st.text_area("Escribe tus observaciones o resumen del informe")

def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="HidroClima PRO - Informe Hidrometeorológico\n\n")
    pdf.multi_cell(0, 10, txt=f"Resumen del Usuario:\n{user_notes}\n\n")
    pdf.multi_cell(0, 10, txt="Datos del archivo:\n")
    for i, row in df.head(10).iterrows():
        pdf.cell(0, 10, txt=str(row.to_dict()), ln=1)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def generar_word():
    doc = Document()
    doc.add_heading('Informe Hidrometeorológico - HidroClima PRO', 0)
    doc.add_paragraph("\nResumen del Usuario:")
    doc.add_paragraph(user_notes)
    doc.add_paragraph("\nDatos del archivo:")
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for index, row in df.head(10).iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

col1, col2 = st.columns(2)
with col1:
    if st.button("📄 Exportar a PDF"):
        try:
            pdf_file = generar_pdf()
            st.download_button("Descargar PDF", pdf_file, file_name="informe_hidroclima.pdf")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

with col2:
    if st.button("📝 Exportar a Word"):
        try:
            word_file = generar_word()
            st.download_button("Descargar Word", word_file, file_name="informe_hidroclima.docx")
        except Exception as e:
            st.error(f"Error al generar Word: {e}")

else: st.info("📌 Por favor, sube un archivo para comenzar.")

