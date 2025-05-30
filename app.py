import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime

# ---------------- CONFIG ------------------
st.set_page_config(page_title="Panel Administrador HidroMet", layout="wide")

# ---------------- SESSION STATE ------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ''

# ----------------- LOGIN -------------------
def login():
    st.title("🔐 Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_btn = st.button("Entrar")

    if login_btn:
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success(f"Login exitoso. Bienvenido, {username}")
        else:
            st.error("❌ Credenciales inválidas")

# ----------------- LOGOUT -------------------
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ''
    st.rerun()

# ----------------- PDF EXPORT -------------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos HidroMet", ln=True, align="C")
    pdf.ln(10)

    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.multi_cell(0, 10, txt=row)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# ----------------- WORD EXPORT -------------------
def export_word(df):
    doc = Document()
    doc.add_heading('Informe de Datos HidroMet', 0)

    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, column in enumerate(df.columns):
        hdr_cells[i].text = str(column)

    for index, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, value in enumerate(row):
            row_cells[i].text = str(value)

    word_output = BytesIO()
    doc.save(word_output)
    word_output.seek(0)
    return word_output

# ----------------- ADMIN TOOLS -------------------
def admin_tools(df):
    st.sidebar.title("🛠 Herramientas de Administración")

    st.subheader("📊 Vista General de Datos")
    st.dataframe(df)

    st.subheader("📈 Gráficos Interactivos")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        st.plotly_chart(px.line(df, y=col, title=f"{col}"))

    st.subheader("🌐 Mapa de Sensores")
    if {'lat', 'lon'}.issubset(df.columns):
        st.map(df[['lat', 'lon']])

    st.subheader("📌 Correlación entre Variables")
    corr = df[numeric_cols].corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto")
    st.plotly_chart(fig_corr)

    st.subheader("📤 Exportar Informes")
    col1, col2 = st.columns(2)
    with col1:
        if st.download_button("📥 Descargar en PDF", data=export_pdf(df), file_name="informe.pdf"):
            st.success("PDF generado")
    with col2:
        if st.download_button("📥 Descargar en Word", data=export_word(df), file_name="informe.docx"):
            st.success("Word generado")

# ---------------- MAIN -------------------
def main():
    if not st.session_state.authenticated:
        login()
        return

    st.sidebar.title(f"👋 Bienvenido, {st.session_state.username}")
    if st.sidebar.button("Cerrar sesión"):
        logout()

    st.title("📡 Panel de Control Administrador - HidroMet")

    uploaded_file = st.file_uploader("Cargar archivo CSV de sensores", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        admin_tools(df)
    else:
        st.warning("Por favor cargue un archivo para acceder a las herramientas.")

# ---------------- RUN -------------------
main()
                         
