import streamlit as st import pandas as pd from io import BytesIO from docx import Document from fpdf import FPDF import base64

----------------------------- CONFIGURACIÓN DE LA APP -----------------------------

st.set_page_config(page_title="HidroClimaPro", layout="wide")

----------------------------- ESTILO PERSONALIZADO -----------------------------

st.markdown(""" <style> .main { background-color: #f8f9fa; } .css-1d391kg {  /* título / font-size: 2.5rem; font-weight: 700; color: #003566; } .css-10trblm {  / subtítulos */ font-size: 1.3rem; color: #003566; } .stButton>button { background-color: #0077b6; color: white; border-radius: 8px; padding: 0.6em 1em; } .stButton>button:hover { background-color: #023e8a; color: white; } </style> """, unsafe_allow_html=True)

----------------------------- TÍTULO Y DESCRIPCIÓN -----------------------------

st.title("📊 HidroClimaPro - Plataforma de Análisis Hidrometeorológico") st.write("Cargue datos de estaciones y genere informes automáticamente en PDF o Word.")

----------------------------- CARGA DE DATOS -----------------------------

st.sidebar.header("📂 Cargar archivo") uploaded_file = st.sidebar.file_uploader("Seleccione un archivo CSV", type=["csv"])

if uploaded_file: try: df = pd.read_csv(uploaded_file) st.success("✅ Archivo cargado exitosamente.") st.dataframe(df, use_container_width=True) except Exception as e: st.error(f"❌ Error al leer el archivo: {e}") st.stop() else: df = pd.DataFrame({ "Estación": ["Lima Centro", "Callao Puerto", "Chosica"], "Temperatura (°C)": [26.3, 24.8, 28.1], "Humedad (%)": [68, 74, 65], "Precipitación (mm)": [0.0, 1.2, 5.5] }) st.info("⚠️ No se ha cargado archivo. Mostrando datos de ejemplo.") st.dataframe(df, use_container_width=True)

----------------------------- EXPORTAR INFORMES -----------------------------

st.markdown("""---""") st.subheader("📤 Exportar informe")

col1, col2 = st.columns(2)

with col1: if st.button("📄 Exportar a Word"): try: doc = Document() doc.add_heading("Informe Hidrometeorológico", level=1) doc.add_paragraph("Datos generados automáticamente por el sistema.") doc.add_paragraph()

table = doc.add_table(rows=1, cols=len(df.columns))
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)

        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)

        word_output = BytesIO()
        doc.save(word_output)
        word_output.seek(0)

        b64 = base64.b64encode(word_output.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe_hidrometeorologico.docx">📄 Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al exportar Word: {e}")

with col2: class PDF(FPDF): def header(self): self.set_font("Arial", "B", 12) self.cell(0, 10, "Informe Hidrometeorológico", ln=True, align="C") self.ln(10)

def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

if st.button("🧾 Exportar a PDF"):
    try:
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        col_widths = [190 / len(df.columns)] * len(df.columns)

        for i, col in enumerate(df.columns):
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(col_widths[i], 10, str(col), border=1, fill=True)
        pdf.ln()

        for _, row in df.iterrows():
            for i, item in enumerate(row):
                pdf.cell(col_widths[i], 10, str(item), border=1)
            pdf.ln()

        pdf_output = BytesIO()
        pdf_output_bytes = pdf.output(dest='S').encode('latin1')
        pdf_output.write(pdf_output_bytes)
        pdf_output.seek(0)

        b64 = base64.b64encode(pdf_output.read()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="informe_hidrometeorologico.pdf">🧾 Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al exportar PDF: {e}")

