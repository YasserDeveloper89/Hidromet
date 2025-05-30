import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime
import os

# Configurar página
st.set_page_config(page_title="Panel Hidromet Admin", layout="wide")

# Usuarios y contraseñas
USERS = {
    "admin": "admin123",
    "tecnico": "tec456"
}

# Funciones de autenticación
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        return

    st.title("Inicio de sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Login exitoso. Bienvenido, {username}")
        else:
            st.error("Credenciales inválidas")
            st.stop()
    st.stop()

# Funciones de cierre de sesión
def logout():
    if st.button("Cerrar sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Exportar a Word
def export_to_word(df):
    doc = Document()
    doc.add_heading("Informe de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, cell in enumerate(row):
            row_cells[i].text = str(cell)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    st.download_button("Descargar Word", buffer, file_name="informe.docx")

# Exportar a PDF
def export_to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.cell(200, 10, txt=row, ln=True)
    buffer = BytesIO()
    pdf.output(name="informe.pdf")
    with open("informe.pdf", "rb") as f:
        st.download_button("Descargar PDF", f, file_name="informe.pdf")

# Panel del administrador
def admin_panel():
    st.title("Panel de Administrador")
    logout()

    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.subheader("Vista previa de datos")
            st.dataframe(df)

            export_to_word(df)
            export_to_pdf(df)

            st.subheader("Gráficos Interactivos")
            numeric_df = df.select_dtypes(include=np.number)
            if not numeric_df.empty:
                fig_corr = px.imshow(numeric_df.corr(), text_auto=True)
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("No hay datos numéricos para graficar")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.info("Por favor cargue un archivo para acceder a las herramientas")

# Main
def main():
    login()
    if st.session_state.username == "admin":
        admin_panel()
    else:
        st.write("Bienvenido usuario técnico. Próximamente módulo disponible.")

if __name__ == "__main__":
    main()
    
