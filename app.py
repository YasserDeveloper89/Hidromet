import streamlit as st import pandas as pd import numpy as np from io import BytesIO from docx import Document from fpdf import FPDF import plotly.graph_objects as go from datetime import datetime

--- Estilo base ---

st.set_page_config(page_title="HidroClimaPro", layout="wide")

st.markdown(""" <style> body { background-color: #f7f9fc; color: #1c1e21; } .main .block-container { padding-top: 2rem; padding-bottom: 2rem; } .stButton button { background-color: #0e76a8; color: white; border: None; padding: 0.6rem 1.2rem; border-radius: 6px; font-size: 1rem; font-weight: bold; } .stButton button:hover { background-color: #095f88; color: white; } </style> """, unsafe_allow_html=True)

--- Encabezado ---

st.title("🌦️ HidroClimaPro - Plataforma de Monitoreo y Análisis") st.markdown(""" Bienvenido a HidroClimaPro

Una plataforma profesional e intuitiva para cargar, analizar y exportar datos climáticos. Ideal para empresas, ingenieros y entidades de monitoreo. """)

--- Subida de archivo ---

st.sidebar.header("📁 Cargar archivo") uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])

if uploaded_file is not None: try: df = pd.read_csv(uploaded_file) st.success("✅ Datos cargados correctamente")

# Vista previa
    st.subheader("🔍 Vista previa de datos")
    st.dataframe(df, use_container_width=True)

    # Análisis rápido
    st.subheader("📊 Análisis general")
    st.write("Filas:", df.shape[0])
    st.write("Columnas:", df.shape[1])
    st.write("Resumen:")
    st.dataframe(df.describe(), use_container_width=True)

    # --- Visualización profesional ---
    st.subheader("📈 Visualización interactiva")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        col_x = st.selectbox("Columna para eje X", df.columns)
        col_y = st.selectbox("Columna para eje Y", numeric_cols)
        chart = go.Figure()
        chart.add_trace(go.Scatter(x=df[col_x], y=df[col_y], mode='lines+markers', name=f'{col_y} vs {col_x}'))
        chart.update_layout(template="plotly_white", height=500, title="Gráfico Interactivo")
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("No se encontraron columnas numéricas para graficar.")

    # --- Generador de informe ---
    st.subheader("📝 Generar Informe")
    comentario = st.text_area("Escribe tu resumen o análisis del informe")

    if st.button("Generar Informe Word y PDF"):
        try:
            # Documento Word
            doc = Document()
            doc.add_heading("Informe de Datos Climáticos", level=1)
            doc.add_paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            doc.add_paragraph("\nResumen del Análisis:")
            doc.add_paragraph(comentario)
            doc.add_paragraph("\nVista previa de datos:")
            doc.add_paragraph(df.head().to_string())
            word_stream = BytesIO()
            doc.save(word_stream)
            word_stream.seek(0)
            st.download_button("📥 Descargar Word", word_stream, file_name="informe_climatico.docx")

            # PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe de Datos Climáticos", ln=1, align='C')
            pdf.cell(200, 10, txt=f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=2)
            pdf.multi_cell(0, 10, txt="Resumen:\n" + comentario)
            pdf.multi_cell(0, 10, txt="Vista previa de datos:\n" + df.head().to_string())
            pdf_stream = BytesIO()
            pdf.output(pdf_stream)
            pdf_stream.seek(0)
            st.download_button("📥 Descargar PDF", pdf_stream, file_name="informe_climatico.pdf")
        except Exception as e:
            st.error(f"Error al generar documentos: {e}")

except Exception as e:
    st.error(f"Error al procesar archivo: {e}")

else: st.info("🔄 Esperando que subas un archivo CSV para comenzar.")

