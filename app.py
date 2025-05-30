import streamlit as st import pandas as pd import base64 from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt import numpy as np

st.set_page_config(page_title="HydroClimaPro", layout="wide")

---------------- SIDEBAR ----------------

st.sidebar.title("HydroClimaPro") st.sidebar.markdown("Versión avanzada para uso institucional")

---------------- HEADER ----------------

st.title("Panel Hidrometeorológico Profesional") st.markdown("""

Cargue su archivo con datos de precipitación, caudal u otros datos meteorológicos.

Formatos soportados: CSV, XLSX

Una vez cargado, podrá analizar, comparar y exportar informes completos. """)


---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader("Cargar archivo de datos", type=["csv", "xlsx"])

data = None if uploaded_file: try: if uploaded_file.name.endswith("csv"): data = pd.read_csv(uploaded_file) else: data = pd.read_excel(uploaded_file) st.success("Archivo cargado correctamente.") st.dataframe(data, use_container_width=True) except Exception as e: st.error(f"Error al procesar el archivo: {e}")

---------------- DATA ANALYSIS MODULES ----------------

if data is not None: st.markdown("---") st.subheader("📊 Análisis de Tendencias") date_columns = [col for col in data.columns if 'fecha' in col.lower() or pd.api.types.is_datetime64_any_dtype(data[col])] numeric_columns = data.select_dtypes(include='number').columns.tolist()

if date_columns and numeric_columns:
    date_col = st.selectbox("Seleccionar columna de fecha", date_columns)
    value_col = st.selectbox("Seleccionar variable para analizar", numeric_columns)

    data[date_col] = pd.to_datetime(data[date_col])
    trend_data = data.groupby(data[date_col].dt.date)[value_col].mean()

    fig, ax = plt.subplots()
    trend_data.plot(ax=ax)
    ax.set_title("Tendencia diaria de " + value_col)
    ax.set_xlabel("Fecha")
    ax.set_ylabel(value_col)
    st.pyplot(fig)

st.markdown("---")
st.subheader(":bar_chart: Comparación entre Ubicaciones")
loc_cols = [col for col in data.columns if 'estacion' in col.lower() or 'zona' in col.lower() or 'ubicacion' in col.lower()]

if loc_cols and numeric_columns:
    loc_col = st.selectbox("Seleccionar columna de ubicación", loc_cols)
    metric = st.selectbox("Seleccionar variable para comparar", numeric_columns)

    compare_data = data.groupby(loc_col)[metric].mean().sort_values(ascending=False)
    st.bar_chart(compare_data)

st.markdown("---")
st.subheader(":rotating_light: Alertas automáticas")
threshold_col = st.selectbox("Seleccionar variable para configurar alerta", numeric_columns)
threshold_value = st.number_input(f"Definir umbral crítico para {threshold_col}", value=float(data[threshold_col].mean() * 1.5))

exceed_data = data[data[threshold_col] > threshold_value]
if not exceed_data.empty:
    st.error(f"Se detectaron {len(exceed_data)} registros que superan el umbral de {threshold_value}")
    st.dataframe(exceed_data)
else:
    st.success("No se detectaron valores críticos.")

st.markdown("---")
st.subheader(":memo: Generar Informe Personalizado")
custom_text = st.text_area("Resumen del informe")

# Exportar PDF
if st.button("Descargar Informe PDF"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="INFORME HIDROMETEOROLÓGICO", ln=True, align="C")
        pdf.ln(10)
        pdf.multi_cell(0, 10, custom_text)

        pdf.ln(10)
        for col in data.columns:
            pdf.cell(40, 10, col, border=1)
        pdf.ln()
        for i in range(min(20, len(data))):
            for col in data.columns:
                pdf.cell(40, 10, str(data.iloc[i][col]), border=1)
            pdf.ln()

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)

        b64 = base64.b64encode(pdf_output.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_hidromet.pdf">Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")

# Exportar Word
if st.button("Descargar Informe Word"):
    try:
        doc = Document()
        doc.add_heading("INFORME HIDROMETEOROLÓGICO", 0)
        doc.add_paragraph(custom_text)

        table = doc.add_table(rows=1, cols=len(data.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(data.columns):
            hdr_cells[i].text = col

        for i in range(min(20, len(data))):
            row_cells = table.add_row().cells
            for j, col in enumerate(data.columns):
                row_cells[j].text = str(data.iloc[i][col])

        word_output = BytesIO()
        doc.save(word_output)
        word_output.seek(0)

        b64 = base64.b64encode(word_output.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_hidromet.docx">Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar el Word: {e}")

