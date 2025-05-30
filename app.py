import streamlit as st import pandas as pd import base64 from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt import numpy as np

Configuración de página

st.set_page_config(page_title="Hidromet Pro", layout="wide")

Estilo del modo claro/oscuro

theme = st.selectbox("Selecciona el tema de la aplicación:", ["Claro", "Oscuro"])

if theme == "Oscuro": st.markdown(""" <style> body { background-color: #0e1117; color: white; } .stTextInput > div > div > input { background-color: #262730; color: white; } .stSelectbox > div > div > select { background-color: #262730; color: white; } </style> """, unsafe_allow_html=True)

st.title("🌧️ Plataforma de Gestión Hidrometeorológica")

uploaded_file = st.file_uploader("📂 Sube tu archivo de datos (CSV o Excel)", type=["csv", "xlsx"])

if uploaded_file is not None: try: if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file, parse_dates=True) else: df = pd.read_excel(uploaded_file, parse_dates=True)

st.success("✅ Archivo cargado correctamente")
    st.subheader("🔍 Vista previa de datos")
    st.dataframe(df)

    # Visualización de datos
    st.subheader("📉 Visualización de datos")

    date_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

    if not date_cols.empty and not numeric_cols.empty:
        date_col = st.selectbox("Selecciona la columna de fecha", date_cols)
        value_col = st.selectbox("Selecciona una columna numérica para graficar", numeric_cols)

        fig, ax = plt.subplots()
        ax.plot(df[date_col], df[value_col])
        ax.set_xlabel(date_col)
        ax.set_ylabel(value_col)
        ax.set_title(f"{value_col} vs {date_col}")
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.warning("⚠️ Se requieren columnas de tipo fecha y numéricas para visualizar.")

    st.subheader("📝 Generar informe")
    informe = st.text_area("Escribe aquí el resumen o conclusiones del informe")

    def generar_pdf(df, informe):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "Informe Hidrometeorológico\n")
        pdf.multi_cell(0, 10, "Resumen del Informe:\n" + informe + "\n\n")

        for col in df.columns:
            pdf.multi_cell(0, 10, f"{col}: {df[col].tolist()[:10]}")
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer

    def generar_word(df, informe):
        doc = Document()
        doc.add_heading('Informe Hidrometeorológico', 0)
        doc.add_paragraph('Resumen del Informe:')
        doc.add_paragraph(informe)

        doc.add_heading('Datos:', level=1)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)

        for index, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, col in enumerate(df.columns):
                row_cells[i].text = str(row[col])

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    if st.button("📄 Descargar Informe en PDF"):
        try:
            pdf_file = generar_pdf(df, informe)
            b64 = base64.b64encode(pdf_file.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe.pdf">📥 Haz clic aquí para descargar el PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")

    if st.button("📝 Descargar Informe en Word"):
        try:
            word_file = generar_word(df, informe)
            b64 = base64.b64encode(word_file.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe.docx">📥 Haz clic aquí para descargar el Word</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")

except Exception as e:
    st.error(f"❌ Error al leer el archivo: {e}")

else: st.info("📎 Por favor, sube un archivo para comenzar.")

