import streamlit as st import pandas as pd import numpy as np from io import BytesIO from docx import Document from fpdf import FPDF import plotly.graph_objects as go from datetime import datetime

✅ Configurar la página (debe ser la primera instrucción Streamlit)

st.set_page_config(page_title="HydroClimaPRO", layout="wide")

🎨 Establecer fondo futurista

def set_background(): st.markdown( f""" <style> .stApp {{ background-image: url("https://images.unsplash.com/photo-1601597111221-06a1b6be9a39?auto=format&fit=crop&w=1950&q=80"); background-size: cover; background-attachment: fixed; color: #FFFFFF; }} .block-container {{ background-color: rgba(0, 0, 0, 0.6); padding: 2rem; border-radius: 1rem; }} </style> """, unsafe_allow_html=True )

set_background()

st.title("📊 HydroClimaPRO - Análisis Avanzado de Datos Climáticos")

📁 Subida de archivo CSV

data_file = st.file_uploader("Carga tu archivo CSV con datos climáticos", type=["csv"])

🔍 Análisis de datos

if data_file is not None: df = pd.read_csv(data_file) st.success("Archivo cargado correctamente") st.subheader("Vista previa de los datos") st.dataframe(df.head())

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

# 📈 Visualización avanzada de datos
st.subheader("📊 Visualización de Datos Interactiva")
selected_col = st.selectbox("Selecciona una columna numérica para graficar:", numeric_cols)

if selected_col:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[selected_col], mode='lines+markers', name=selected_col))
    fig.update_layout(title=f"Visualización de {selected_col}", xaxis_title="Índice", yaxis_title=selected_col,
                      template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# 📊 Estadísticas avanzadas
st.subheader("📊 Estadísticas Generales")
stats = df.describe().transpose()
st.dataframe(stats)

# 📑 Generar informe Word
def create_word_report():
    doc = Document()
    doc.add_heading("Informe de Datos Climáticos - HydroClimaPRO", 0)
    doc.add_paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_heading("Resumen Estadístico", level=1)
    doc.add_paragraph(stats.to_string())
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# 🧾 Generar informe PDF
def create_pdf_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos Climáticos - HydroClimaPRO", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='L')
    pdf.ln(10)
    for col in stats.index:
        row = stats.loc[col]
        line = f"{col}: Media={row['mean']:.2f}, Min={row['min']:.2f}, Max={row['max']:.2f}"
        pdf.cell(200, 10, txt=line, ln=True, align='L')
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# 📥 Botones de descarga
st.subheader("📥 Exportar Informes")
col1, col2 = st.columns(2)
with col1:
    if st.download_button("📄 Descargar Informe Word", data=create_word_report(), file_name="informe_climatico.docx"):
        st.success("Informe Word generado con éxito")
with col2:
    if st.download_button("🧾 Descargar Informe PDF", data=create_pdf_report(), file_name="informe_climatico.pdf"):
        st.success("Informe PDF generado con éxito")

else: st.markdown(""" ### Bienvenido a HydroClimaPRO Esta plataforma avanzada permite: - Cargar y analizar datos climáticos - Visualizar gráficas interactivas - Generar informes profesionales en PDF y Word

Por favor, sube un archivo CSV para comenzar.
""")

