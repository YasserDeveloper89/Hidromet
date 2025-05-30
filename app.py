import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

def set_background():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://stockcake.com/i/futuristic-dashboard-design_1134623_462225");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

st.set_page_config(page_title="HydroClimaPRO", layout="wide")

st.title("🚀 HydroClimaPRO - Análisis Hidrometeorológico Avanzado")

uploaded_file = st.sidebar.file_uploader("📤 Cargar archivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Vista Previa de los Datos")
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    selected_column = st.selectbox("Selecciona una columna numérica para graficar:", numeric_cols)

    if selected_column:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[selected_column],
            mode='lines+markers',
            name=selected_column,
            line=dict(color='cyan', width=2),
            marker=dict(size=6, color='magenta')
        ))
        fig.update_layout(
            title=f"Gráfico de {selected_column}",
            xaxis_title="Índice",
            yaxis_title=selected_column,
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Estadísticas Descriptivas")
    st.write(df[numeric_cols].describe())

    st.subheader("📝 Generar Informe")
    report_text = st.text_area("Resumen del informe", placeholder="Escribe un resumen técnico...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generar_word():
        doc = Document()
        doc.add_heading("Informe Hidrometeorológico", 0)
        doc.add_paragraph(f"Fecha de generación: {timestamp}")
        doc.add_heading("Resumen:", level=1)
        doc.add_paragraph(report_text if report_text else "Sin resumen disponible.")
        doc.add_heading("Estadísticas:", level=1)
        doc.add_paragraph(df.describe().to_string())
        word_file = BytesIO()
        doc.save(word_file)
        word_file.seek(0)
        return word_file

    def generar_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Informe Hidrometeorológico", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(200, 10, f"Fecha: {timestamp}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Resumen:\n{report_text if report_text else 'Sin resumen.'}")
        pdf.ln(10)
        pdf.multi_cell(0, 10, "Estadísticas descriptivas:\n" + df.describe().to_string())
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        return pdf_output

    col1, col2 = st.columns(2)
    with col1:
        word_file = generar_word()
        st.download_button(
            label="📥 Descargar Informe Word",
            data=word_file,
            file_name=f"Informe_{timestamp}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    with col2:
        try:
            pdf_file = generar_pdf()
            st.download_button(
                label="📥 Descargar Informe PDF",
                data=pdf_file,
                file_name=f"Informe_{timestamp}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

else:
    st.markdown("""
    <div style='text-align: center; padding-top: 50px;'>
        <h1 style='color:#2c3e50;'>🚀 Bienvenido a <span style='color:#1abc9c;'>HydroClimaPRO</span></h1>
        <p style='font-size:18px; color:#34495e; max-width:700px; margin:auto;'>
            Una plataforma inteligente para el análisis y generación de informes hidrometeorológicos.
            Carga tus datos en formato CSV y accede a visualizaciones avanzadas, estadísticas detalladas y exportación profesional de reportes.
        </p>
    </div>
    <br><br>
    """, unsafe_allow_html=True)

    st.markdown("### ✅ ¿Qué puedes hacer con esta herramienta?")
    st.markdown("""
    - 📊 Analizar datos de clima y ambiente (temperatura, humedad, lluvia, etc.).
    - 🧮 Visualizar gráficamente tendencias y comparativas.
    - 📥 Exportar informes en formatos **PDF** y **Word** listos para presentación.
    - 📈 Acceder a estadísticas profesionales con solo un clic.
    """)

    st.markdown("### ⬆️ Para comenzar, sube un archivo CSV desde la barra lateral.")
