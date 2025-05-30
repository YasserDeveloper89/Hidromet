import streamlit as st import pandas as pd import base64 from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt import numpy as np

st.set_page_config(page_title="HidroClimaPro", layout="wide")

st.title("🌧️ HidroClimaPro - Plataforma de Análisis Hidrometeorológico")

modo = st.sidebar.radio("Modo de visualización", ["Claro", "Oscuro"]) if modo == "Oscuro": st.markdown(""" <style> body, .reportview-container { background-color: #1e1e1e; color: #f5f5f5; } </style> """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Sube tu archivo de datos (.csv)", type="csv")

if uploaded_file: try: df = pd.read_csv(uploaded_file) st.success("✅ Archivo cargado exitosamente") st.dataframe(df, use_container_width=True)

st.markdown("---")
    st.markdown("### 📊 Análisis Avanzado de Variables")

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    if numeric_cols:
        selected_cols = st.multiselect("Selecciona variables numéricas para analizar", numeric_cols, default=numeric_cols[:2])

        st.subheader("📉 Histogramas")
        for col in selected_cols:
            fig, ax = plt.subplots()
            ax.hist(df[col].dropna(), bins=20, color='skyblue', edgecolor='black')
            ax.set_title(f"Distribución: {col}")
            st.pyplot(fig)

        st.subheader("📦 Boxplots (Valores atípicos)")
        fig, ax = plt.subplots()
        df[selected_cols].plot(kind='box', ax=ax)
        st.pyplot(fig)

        if len(selected_cols) >= 2:
            st.subheader("🔗 Matriz de Correlación")
            corr = df[selected_cols].corr()
            fig, ax = plt.subplots()
            im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
            ax.set_xticks(np.arange(len(selected_cols)))
            ax.set_yticks(np.arange(len(selected_cols)))
            ax.set_xticklabels(selected_cols, rotation=45)
            ax.set_yticklabels(selected_cols)
            fig.colorbar(im)
            st.pyplot(fig)

        st.subheader("📊 Comparador Multivariable")
        fig, ax = plt.subplots()
        df[selected_cols].plot(ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No se encontraron columnas numéricas para análisis.")

    st.markdown("---")
    st.markdown("### 📝 Generar Informe")
    resumen = st.text_area("Escribe tu resumen del informe")

    if st.button("📥 Exportar Informe PDF"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align="C")
            pdf.ln(10)
            pdf.multi_cell(0, 10, resumen)
            pdf.ln(10)

            for i in range(len(df)):
                row = ", ".join(f"{col}: {df[col][i]}" for col in df.columns)
                pdf.multi_cell(0, 10, row)

            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            b64_pdf = base64.b64encode(pdf_output.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="informe.pdf">📄 Descargar PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")

    if st.button("📝 Exportar Informe Word"):
        try:
            doc = Document()
            doc.add_heading("Informe Hidrometeorológico", 0)
            doc.add_paragraph(resumen)
            doc.add_paragraph("\nDatos:")
            table = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = col
            for i in range(len(df)):
                row_cells = table.add_row().cells
                for j, col in enumerate(df.columns):
                    row_cells[j].text = str(df[col][i])

            word_output = BytesIO()
            doc.save(word_output)
            word_output.seek(0)

            b64_word = base64.b64encode(word_output.read()).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="informe.docx">📝 Descargar Word</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")

except Exception as e:
    st.error(f"Error al leer el archivo: {e}")

