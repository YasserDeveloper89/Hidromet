import streamlit as st import pandas as pd import numpy as np from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt import plotly.express as px from datetime import datetime

st.set_page_config(page_title="Hidromet PRO", layout="wide")

st.markdown(""" <style> .main {background-color: #f9f9f9;} div.block-container {padding-top: 2rem; padding-bottom: 2rem;} h1, h2, h3 {color: #0e1117;} </style> """, unsafe_allow_html=True)

st.title("🌦️ Hidromet PRO - Análisis Hidroclimático Avanzado")

File uploader

uploaded_file = st.file_uploader("📁 Sube un archivo CSV", type=["csv"]) if uploaded_file: try: df = pd.read_csv(uploaded_file)

st.markdown("## 🗂️ Vista previa de los datos")
    st.dataframe(df.head(50), use_container_width=True)

    st.markdown("## 📊 Análisis de datos")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    time_cols = df.select_dtypes(include='object').columns.tolist()

    if numeric_cols:
        col_to_plot = st.selectbox("Selecciona una columna numérica para visualizar:", numeric_cols)
        if col_to_plot:
            st.markdown("### 📈 Gráfico de línea interactivo")
            df_sorted = df.sort_values(by=time_cols[0]) if time_cols else df.copy()
            fig = px.line(df_sorted, x=time_cols[0] if time_cols else df.index, y=col_to_plot, title=f"Tendencia de {col_to_plot}", markers=True)
            st.plotly_chart(fig, use_container_width=True)

            # KPI-style summary
            st.markdown("### 🔍 Indicadores clave")
            col1, col2, col3 = st.columns(3)
            col1.metric("Media", f"{df[col_to_plot].mean():.2f}")
            col2.metric("Máximo", f"{df[col_to_plot].max():.2f}")
            col3.metric("Mínimo", f"{df[col_to_plot].min():.2f}")

    st.markdown("## 📝 Generar informe personalizado")
    informe = st.text_area("Escribe aquí tu resumen del informe")

    # Exportar PDF
    if st.button("📤 Exportar a PDF"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe Hidromet PRO", ln=True, align="C")
            pdf.ln(10)
            pdf.multi_cell(0, 10, informe)
            pdf.ln(5)
            pdf.set_font("Arial", size=10)
            for col in df.columns:
                pdf.cell(40, 10, col, border=1)
            pdf.ln()
            for i in range(min(len(df), 20)):
                for col in df.columns:
                    val = str(df.iloc[i][col])
                    pdf.cell(40, 10, val[:15], border=1)
                pdf.ln()
            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            st.download_button(label="📄 Descargar PDF", data=pdf_buffer, file_name="informe_hidromet.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

    # Exportar Word
    if st.button("📝 Exportar a Word"):
        try:
            doc = Document()
            doc.add_heading("Informe Hidromet PRO", 0)
            doc.add_paragraph(informe)
            doc.add_heading("Vista previa de datos:", level=1)
            t = doc.add_table(df.shape[0]+1, df.shape[1])
            for j in range(df.shape[1]):
                t.cell(0, j).text = df.columns[j]
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    t.cell(i+1, j).text = str(df.values[i, j])
            word_buffer = BytesIO()
            doc.save(word_buffer)
            word_buffer.seek(0)
            st.download_button(label="📄 Descargar Word", data=word_buffer, file_name="informe_hidromet.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.error(f"Error al generar Word: {e}")
except Exception as e:
    st.error(f"Error al procesar el archivo: {e}")

else: st.info("Por favor, sube un archivo CSV para comenzar.")

