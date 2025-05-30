import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="HydroClimaPRO", layout="wide")

# --- Estilos personalizados ---
st.markdown("""
    <style>
        .main {
            background-color: #f4f6f9;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .css-1aumxhk {
            background-color: #ffffff !important;
        }
        .stButton>button {
            color: white;
            background: #2c3e50;
            border-radius: 10px;
            font-size: 16px;
            height: 3em;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("HydroClimaPRO")
uploaded_file = st.sidebar.file_uploader("📤 Cargar archivo CSV", type=["csv"])
st.sidebar.markdown("---")

# --- Función para cargar y limpiar datos ---
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df

# --- Visualización inicial de datos ---
if uploaded_file:
    df = load_data(uploaded_file)
    st.title("📊 Panel de Análisis Hidrometeorológico")

    st.subheader("Vista previa de datos")
    st.dataframe(df.head(10), use_container_width=True)

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    date_cols = df.select_dtypes(include=["object", "datetime"]).columns.tolist()

    # --- Análisis estadístico ---
    st.subheader("📈 Análisis Estadístico General")
    st.dataframe(df.describe(), use_container_width=True)

    # --- Visualización gráfica ---
    st.subheader("📉 Visualización de Datos")
    selected_column = st.selectbox("Selecciona una columna numérica para graficar:", numeric_cols)

    if selected_column:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df[selected_column], mode="lines+markers", name=selected_column))
        fig.update_layout(title=f"Gráfico de {selected_column}", xaxis_title="Índice", yaxis_title=selected_column)
        st.plotly_chart(fig, use_container_width=True)

    # --- Funciones estadísticas PRO ---
    st.subheader("📊 Herramientas Avanzadas")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Valor Máximo", f"{df[selected_column].max():,.2f}")

    with col2:
        st.metric("Valor Mínimo", f"{df[selected_column].min():,.2f}")

    with col3:
        st.metric("Media", f"{df[selected_column].mean():,.2f}")

    st.markdown("---")

    # --- Generación de informe ---
    st.subheader("📝 Generar Informe")
    observaciones = st.text_area("Resumen o comentario adicional para el informe:", height=150)

    if st.button("🧾 Generar Documento"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Crear documento Word
        word_doc = Document()
        word_doc.add_heading("Informe Hidrometeorológico", level=1)
        word_doc.add_paragraph(f"Fecha de generación: {now}")
        word_doc.add_paragraph(observaciones)
        word_doc.add_heading("Datos principales:", level=2)
        word_table = word_doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = word_table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = col
        for index, row in df.iterrows():
            row_cells = word_table.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
        word_buffer = BytesIO()
        word_doc.save(word_buffer)
        word_buffer.seek(0)

        st.download_button("📥 Descargar Informe Word", word_buffer, file_name="informe.docx")

        # Crear PDF
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt=f"Fecha de generación: {now}\n\n{observaciones}")

            pdf.ln(10)
            for col in df.columns:
                pdf.cell(40, 10, txt=str(col), border=1)
            pdf.ln()
            for _, row in df.iterrows():
                for val in row:
                    pdf.cell(40, 10, txt=str(val)[:15], border=1)
                pdf.ln()

            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            st.download_button("📥 Descargar Informe PDF", pdf_buffer, file_name="informe.pdf")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

else:
    st.info("Por favor, carga un archivo CSV para comenzar.")
