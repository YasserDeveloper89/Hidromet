import streamlit as st import pandas as pd import numpy as np import base64 from io import BytesIO from docx import Document from fpdf import FPDF import matplotlib.pyplot as plt from datetime import datetime

st.set_page_config(layout="wide", page_title="HydroClima Pro", page_icon="🌧️")

Initialize session state

if 'theme' not in st.session_state: st.session_state.theme = 'Light'

Theme toggle

with st.sidebar: st.markdown("## Ajustes") theme_toggle = st.selectbox("Tema de la aplicación", ["Light", "Dark"]) st.session_state.theme = theme_toggle uploaded_file = st.file_uploader("Sube tu archivo de datos hidrometeorológicos (.csv)", type=["csv"])

Apply dark theme style manually

if st.session_state.theme == "Dark": st.markdown( """ <style> body { background-color: #1E1E1E; color: white; } .stTextInput, .stSelectbox, .stButton > button { background-color: #333 !important; color: white; } </style> """, unsafe_allow_html=True )

Title

st.title("🌦️ HydroClima PRO - Sistema de Análisis Hidrometeorológico Avanzado") st.markdown("""---""")

Sidebar navigation

menu = st.sidebar.radio("Secciones", [ "📊 Dashboard General", "🔍 Comparación de Períodos", "📉 Análisis de Anomalías", "📈 Visualización Avanzada", "🧠 Informe Automático", "📤 Exportar Informes", "📚 Historial de Análisis" ])

Load data

if uploaded_file: df = pd.read_csv(uploaded_file) df.columns = df.columns.str.strip() df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce') numeric_cols = df.select_dtypes(include=np.number).columns.tolist() else: df = pd.DataFrame()

Dashboard General

if menu == "📊 Dashboard General" and not df.empty: st.subheader("Resumen de Indicadores") col1, col2, col3 = st.columns(3) with col1: st.metric("🌡️ Temperatura Media (°C)", f"{df[numeric_cols[0]].mean():.2f}") with col2: st.metric("💧 Precipitación Total (mm)", f"{df[numeric_cols[1]].sum():.1f}") with col3: st.metric("🌫️ Humedad Media (%)", f"{df[numeric_cols[2]].mean():.1f}")

Comparador de Periodos

if menu == "🔍 Comparación de Períodos" and not df.empty: st.subheader("Comparar dos rangos de fechas") d1 = st.date_input("Inicio Periodo A", df['Fecha'].min()) d2 = st.date_input("Fin Periodo A", df['Fecha'].max()) d3 = st.date_input("Inicio Periodo B", df['Fecha'].min()) d4 = st.date_input("Fin Periodo B", df['Fecha'].max())

a = df[(df['Fecha'] >= pd.to_datetime(d1)) & (df['Fecha'] <= pd.to_datetime(d2))]
b = df[(df['Fecha'] >= pd.to_datetime(d3)) & (df['Fecha'] <= pd.to_datetime(d4))]

diff_temp = a[numeric_cols[0]].mean() - b[numeric_cols[0]].mean()
st.info(f"Diferencia de temperatura media: {diff_temp:.2f} °C")

fig, ax = plt.subplots()
ax.plot(a['Fecha'], a[numeric_cols[0]], label="Periodo A")
ax.plot(b['Fecha'], b[numeric_cols[0]], label="Periodo B")
ax.legend()
st.pyplot(fig)

Análisis de Anomalías

if menu == "📉 Análisis de Anomalías" and not df.empty: st.subheader("Detección de Anomalías") col = st.selectbox("Selecciona columna a analizar", numeric_cols) z = (df[col] - df[col].mean()) / df[col].std() df['Anómalo'] = z.abs() > 2 st.dataframe(df[df['Anómalo']])

Visualización avanzada

if menu == "📈 Visualización Avanzada" and not df.empty: st.subheader("Visualización de Múltiples Variables") selected = st.multiselect("Selecciona columnas", numeric_cols, default=numeric_cols) fig, ax = plt.subplots() for c in selected: ax.plot(df['Fecha'], df[c], label=c) ax.legend() st.pyplot(fig)

Informe Automático

if menu == "🧠 Informe Automático" and not df.empty: st.subheader("Resumen de Informe Automático") resumen = f"Durante el período de análisis, se registró una temperatura media de {df[numeric_cols[0]].mean():.2f}°C, una precipitación acumulada de {df[numeric_cols[1]].sum():.1f} mm y una humedad relativa media de {df[numeric_cols[2]].mean():.1f}%." st.text_area("Informe generado:", resumen, height=150)

Exportar informes

if menu == "📤 Exportar Informes" and not df.empty: st.subheader("Exportar informe profesional") informe_texto = st.text_area("Texto del informe", "Análisis de datos hidrometeorológicos detallado...", height=150)

def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, informe_texto)
    pdf.ln()
    for col in df.columns:
        pdf.cell(40, 10, col, 1)
    pdf.ln()
    for i in df.head(20).itertuples(index=False):
        for v in i:
            pdf.cell(40, 10, str(v), 1)
        pdf.ln()
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

def export_word():
    doc = Document()
    doc.add_heading("Informe Hidrometeorológico", 0)
    doc.add_paragraph(informe_texto)
    t = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = t.rows[0].cells
    for i, c in enumerate(df.columns):
        hdr_cells[i].text = c
    for row in df.head(20).values.tolist():
        row_cells = t.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    b = BytesIO()
    doc.save(b)
    return b.getvalue()

col1, col2 = st.columns(2)
with col1:
    if st.download_button("📥 Descargar PDF", data=export_pdf(), file_name="informe.pdf"):
        st.success("PDF generado")
with col2:
    if st.download_button("📥 Descargar Word", data=export_word(), file_name="informe.docx"):
        st.success("Word generado")

Historial

if menu == "📚 Historial de Análisis": st.subheader("Historial disponible próximamente") st.info("En futuras versiones podrás consultar y volver a generar informes anteriores automáticamente.")

