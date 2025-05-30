import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Hidromet Pro", layout="wide")

# ======== Modo Claro / Oscuro =========
theme = st.sidebar.radio("🎨 Modo de visualización", ["Claro", "Oscuro"])
is_dark = theme == "Oscuro"
bg_color = "#1e1e1e" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#000000"

st.markdown(f"""
    <style>
    html, body, [class*="css"]  {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    .stButton > button {{
        background-color: {'#444' if is_dark else '#007bff'};
        color: white;
    }}
    .stTextInput input {{
        background-color: {'#333' if is_dark else 'white'};
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🌧️ Hidromet Pro - Plataforma de Análisis y Reporte de Datos")

uploaded_file = st.file_uploader("📤 Cargar archivo CSV", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Archivo cargado correctamente.")
        st.dataframe(df)

        st.subheader("📈 Visualización de Datos")
        column = st.selectbox("Selecciona columna para graficar", df.columns)

        try:
            df[column] = pd.to_numeric(df[column])
        except:
            pass

        if pd.api.types.is_numeric_dtype(df[column]):
            fig, ax = plt.subplots()
            ax.plot(df[column], color='cyan' if is_dark else 'blue')
            ax.set_title(f"Evolución de {column}", color=text_color)
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            ax.tick_params(colors=text_color)
            st.pyplot(fig)
        elif pd.api.types.is_datetime64_any_dtype(df[column]) or column.lower() == "fecha":
            if "Fecha" in df.columns:
                df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
                numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
                if numeric_columns:
                    y_col = st.selectbox("Columna numérica para graficar vs Fecha", numeric_columns)
                    fig, ax = plt.subplots()
                    ax.plot(df["Fecha"], df[y_col], color='orange')
                    ax.set_title(f"{y_col} vs Fecha", color=text_color)
                    fig.patch.set_facecolor(bg_color)
                    ax.set_facecolor(bg_color)
                    ax.tick_params(colors=text_color)
                    st.pyplot(fig)
                else:
                    st.warning("No hay columnas numéricas disponibles.")
            else:
                st.warning("No se encontró una columna 'Fecha' válida.")
        else:
            st.warning("Columna no numérica. No se puede graficar.")

        st.subheader("📝 Generar Informe Personalizado")
        resumen = st.text_area("Resumen del informe")

        # ===== Función PDF =====
        def generar_pdf(df, resumen):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "Informe Hidrometeorológico", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 10, resumen)
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 10)
            for col in df.columns:
                pdf.cell(40, 8, str(col), border=1)
            pdf.ln()
            pdf.set_font("Arial", '', 8)
            for _, row in df.iterrows():
                for item in row:
                    pdf.cell(40, 8, str(item), border=1)
                pdf.ln()
            return pdf.output(dest='S').encode('latin1')

        # ===== Función Word =====
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
            word_io = BytesIO()
            doc.save(word_io)
            word_io.seek(0)
            return word_io.read()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Descargar PDF"):
                try:
                    pdf_bytes = generar_pdf(df, resumen)
                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="informe.pdf">📥 Haz clic para descargar PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error al generar PDF: {e}")

        with col2:
            if st.button("📝 Descargar Word"):
                try:
                    word_bytes = generar_word(df, resumen)
                    b64_word = base64.b64encode(word_bytes).decode()
                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="informe.docx">📝 Haz clic para descargar Word</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error al generar Word: {e}")

    except Exception as e:
        st.error(f"❌ Error general al procesar el archivo: {e}")
else:
    st.info("📂 Por favor, sube un archivo CSV para comenzar.")
