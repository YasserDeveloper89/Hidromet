import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime
import base64

# --- Simulación de credenciales ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tecnico123", "role": "tecnico"},
    "visualizador": {"password": "visual123", "role": "visualizador"},
}

def set_logged_in(user):
    st.session_state.logged_in = True
    st.session_state.username = user
    st.session_state.role = USERS[user]["role"]

def logout():
    st.session_state.clear()
    st.experimental_set_query_params()

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Inicio de Sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            if username in USERS and USERS[username]["password"] == password:
                set_logged_in(username)
                st.success(f"Login exitoso. Bienvenido, {username}")
            else:
                st.error("Credenciales inválidas")
        st.stop()

# --- Funciones para exportar ---
def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for i in range(len(df)):
            row = ', '.join([str(x) for x in df.iloc[i]])
            pdf.cell(200, 10, txt=row, ln=True)
        temp_filename = "informe.pdf"
        pdf.output(temp_filename)
        with open(temp_filename, "rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">📄 Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

def export_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe de Datos", 0)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, column in enumerate(df.columns):
            hdr_cells[i].text = column
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, cell in enumerate(row):
                row_cells[i].text = str(cell)
        temp_filename = "informe.docx"
        doc.save(temp_filename)
        with open(temp_filename, "rb") as f:
            word_bytes = f.read()
        b64 = base64.b64encode(word_bytes).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">📝 Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

def admin_panel():
    st.title("📊 Panel de Control - Administrador")
    uploaded_file = st.file_uploader("📁 Cargar archivo CSV", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo cargado exitosamente.")
            st.subheader("📄 Vista previa de los datos")
            st.dataframe(df)

            st.subheader("📈 Gráficos interactivos")
            numeric_cols = df.select_dtypes(include=[np.number])
            if not numeric_cols.empty:
                fig_line = px.line(numeric_cols, title="Tendencias de Variables")
                st.plotly_chart(fig_line)

                fig_bar = px.bar(numeric_cols, title="Resumen de Variables")
                st.plotly_chart(fig_bar)
            else:
                st.warning("No hay columnas numéricas para mostrar gráficos.")

            st.subheader("📤 Exportar Informe")
            export_pdf(df)
            export_word(df)
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")

def main():
    login()

    if st.session_state.role == "admin":
        admin_panel()
    else:
        st.warning("Acceso restringido solo para administradores.")

    if st.button("Cerrar sesión"):
        logout()

if __name__ == "__main__":
    main()
    
