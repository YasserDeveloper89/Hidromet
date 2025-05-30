import streamlit as st import pandas as pd import base64 from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt import numpy as np

Configuración inicial

st.set_page_config(page_title="Hidromet Pro", layout="wide")

Modo claro/oscuro

modo = st.sidebar.selectbox("Modo de visualización", ["Claro", "Oscuro"]) if modo == "Oscuro": st.markdown(""" <style> body { background-color: #111; color: #eee; } .stApp { background-color: #111; } </style> """, unsafe_allow_html=True)

Encabezado principal

st.title("🌦️ Plataforma Hidromet Pro") st.markdown("Una herramienta avanzada para análisis hidrometeorológico.")

Subida de archivo

uploaded_file = st.file_uploader("Sube un archivo CSV con datos meteorológicos o hidrológicos", type="csv")

if uploaded_file: try: df = pd.read_csv(uploaded_file) st.success("Archivo cargado correctamente") st.dataframe(df)

# Análisis rápido
    st.subheader("Estadísticas rápidas")
    st.write(df.describe())

    # Visualización
    st.subheader("Visualización de datos")
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if numeric_columns:
        column_to_plot = st.selectbox("Selecciona una columna numérica para visualizar", numeric_columns)
        plt.figure(figsize=(10, 4))
        plt.plot(df[column_to_plot])
        plt.title(f"Evolución de {column_to_plot}")
        plt.xlabel("Índice")
        plt.ylabel(column_to_plot)
        st.pyplot(plt)
    else:
        st.warning("No se encontraron columnas numéricas para graficar.")

    # Generación de informe
    st.subheader("📝 Generar informe")
    informe_texto = st.text_area("Redacta tu informe aquí")

    def generar_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "Informe Hidromet Pro")
        pdf.ln()
        pdf.multi_cell(0, 10, informe_texto)
        pdf.ln()
        pdf.multi_cell(0, 10, "Resumen de datos:")
        for col in df.columns:
            pdf.multi_cell(0, 10, f"{col}: {df[col].describe().to_dict()}")
        output = BytesIO()
        pdf.output(output)
        return output

    def generar_word():
        doc = Document()
        doc.add_heading('Informe Hidromet Pro', 0)
        doc.add_paragraph(informe_texto)
        doc.add_heading('Resumen de datos', level=1)
        for col in df.columns:
            stats = df[col].describe().to_dict()
            doc.add_paragraph(f"{col}: {stats}")
        output = BytesIO()
        doc.save(output)
        return output

    if st.button("📥 Descargar informe en PDF"):
        try:
            pdf_bytes = generar_pdf()
            st.download_button(
                label="Descargar PDF",
                data=pdf_bytes.getvalue(),
                file_name="informe_hidromet.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")

    if st.button("📥 Descargar informe en Word"):
        try:
            word_bytes = generar_word()
            st.download_button(
                label="Descargar Word",
                data=word_bytes.getvalue(),
                file_name="informe_hidromet.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")

except Exception as e:
    st.error(f"Error al cargar archivo: {e}")

else: st.info("Por favor, sube un archivo para comenzar.")

