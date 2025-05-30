import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime

# -------------------- Autenticación -------------------- #
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tecnico123", "role": "tecnico"},
    "cliente": {"password": "cliente123", "role": "cliente"}
}

# Inicializar estado de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# -------------------- Funciones auxiliares -------------------- #
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.experimental_rerun()

def login():
    st.title("Inicio de sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.success(f"Login exitoso. Bienvenido, {username}")
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas")

# -------------------- Exportar a PDF -------------------- #
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos", ln=True, align='C')
    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.cell(200, 10, txt=row, ln=True)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# -------------------- Exportar a Word -------------------- #
def export_word(df):
    doc = Document()
    doc.add_heading('Informe de Datos', 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, column in enumerate(df.columns):
        hdr_cells[i].text = str(column)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    word_output = BytesIO()
    doc.save(word_output)
    word_output.seek(0)
    return word_output

# -------------------- Panel de administrador -------------------- #
def admin_panel():
    st.title("Panel de Administración")
    st.write(f"Bienvenido, {st.session_state.username}")
    uploaded_file = st.file_uploader("Cargar archivo CSV", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.subheader("Vista Previa de los Datos")
            st.dataframe(df)

            st.subheader("📊 Estadísticas básicas")
            st.write(df.describe())

            st.subheader("📈 Gráficos Interactivos")
            numeric_cols = df.select_dtypes(include=np.number).columns
            if len(numeric_cols) > 1:
                st.plotly_chart(px.line(df[numeric_cols]))
                st.plotly_chart(px.box(df[numeric_cols]))
            else:
                st.warning("No hay suficientes columnas numéricas para graficar.")

            st.subheader("📄 Exportar Informes")
            col1, col2 = st.columns(2)
            with col1:
                if st.download_button("Descargar PDF", export_pdf(df), file_name="informe.pdf"):
                    st.success("PDF generado correctamente")
            with col2:
                if st.download_button("Descargar Word", export_word(df), file_name="informe.docx"):
                    st.success("Documento Word generado correctamente")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        st.warning("Por favor cargue un archivo para acceder a las herramientas")

# -------------------- Main -------------------- #
def main():
    if not st.session_state.logged_in:
        login()
    else:
        if st.button("Cerrar sesión"):
            logout()
        if st.session_state.role == "admin":
            admin_panel()
        else:
            st.error("Acceso denegado. Solo los administradores pueden acceder a esta sección.")

if __name__ == "__main__":
    main()
            
