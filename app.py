import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np

# Configuración inicial
st.set_page_config(page_title="Hidromet Pro", layout="wide")

# Toggle de tema visual
theme = st.sidebar.radio("🎨 Modo de visualización", ["Claro", "Oscuro"])

bg_color = "#FFFFFF" if theme == "Claro" else "#1e1e1e"
text_color = "#000000" if theme == "Claro" else "#FFFFFF"

st.markdown(f"""
    <style>
    body {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🌦️ Hidromet Pro - Análisis y Exportación de Datos Hidrometeorológicos")

uploaded_file = st.file_uploader("📥 Cargar archivo CSV", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Archivo cargado correctamente.")
        st.dataframe(df)

        st.subheader("📊 Visualización de Datos")
        column = st.selectbox("Selecciona columna para graficar", df.columns)
        if pd.api.types.is_numeric_dtype(df[column]):
            fig, ax = plt.subplots()
            ax.plot(df[column], color="cyan" if theme == "Oscuro" else "blue")
            ax.set_title(f"Evolución de {column}", color=text_color)
            ax.set_facecolor(bg_color)
            ax.tick_params(axis='x', colors=text_color)
            ax.tick_params(axis='y', colors=text_color)
            st.pyplot(fig)
        else:
            st.warning("⚠️ La columna seleccionada no contiene datos numéricos.")

        st.subheader("📈 Análisis Estadístico")
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        if numeric_columns:
            analysis_column = st.selectbox("Selecciona columna numérica", numeric_columns)
            stats = df[analysis_column].describe()
            st.write(stats)
            fig_hist, ax_hist = plt.subplots()
            ax_hist.hist(df[analysis_column], bins=20, color='skyblue', edgecolor='black')
            st.pyplot(fig_hist)
        else:
            st.info("No hay columnas numéricas disponibles.")

        st.subheader("📝 Generar Informe")
        resumen = st.text_area("Resumen del informe")

        def generar_pdf(df, resumen):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "Informe Hidrometeorológico", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, resumen)
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 10)
            for col in df.columns:
                pdf.cell(40, 8, str(col), border=1)
            pdf.ln()

            pdf.set_font("Arial", size=8)
            for _, row in df.iterrows():
                for item in row:
                    pdf.cell(40, 8, str(item), border=1)
                pdf.ln()

            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            return pdf_buffer

        def generar_word(df, resumen):
            doc = Document()
            doc.add_heading("Informe Hidrometeorológico", 0)
            doc.add_paragraph(resumen)

            table = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = str(col)

            for _, row in df.iterrows():
                row_cells = table.add_row().cells
                for i, item in enumerate(row):
                    row_cells[i].text = str(item)

            word_buffer = BytesIO()
            doc.save(word_buffer)
            word_buffer.seek(0)
            return word_buffer

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Descargar PDF"):
                try:
                    pdf_bytes = generar_pdf(df, resumen)
                    b64_pdf = base64.b64encode(pdf_bytes.read()).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="informe.pdf">📄 Haz clic aquí para descargar el PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error al generar PDF: {e}")

        with col2:
            if st.button("📝 Descargar Word"):
                try:
                    word_bytes = generar_word(df, resumen)
                    b64_word = base64.b64encode(word_bytes.read()).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64_word}" download="informe.docx">📝 Haz clic aquí para descargar el Word</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error al generar Word: {e}")

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
else:
    st.info("🔁 Esperando que subas un archivo CSV para comenzar.")
