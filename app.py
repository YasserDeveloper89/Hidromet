import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime

# --- Simulación de base de datos de usuarios ---
USERS_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tecnico123", "role": "tecnico"},
    "analista": {"password": "analista123", "role": "analista"},
}

# --- Estado de sesión ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.username = ""
    st.session_state.role = ""

def login():
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        user = USERS_DB.get(username)
        if user and user["password"] == password:
            st.session_state.auth = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas")

def logout():
    st.session_state.auth = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.experimental_rerun()

def export_to_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos", ln=1, align="C")
        for i, row in df.iterrows():
            row_text = ', '.join([str(x) for x in row])
            pdf.cell(200, 10, txt=row_text, ln=1, align="L")
        buffer = BytesIO()
        pdf.output(buffer)
        st.download_button("Descargar PDF", buffer.getvalue(), file_name="informe.pdf")
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

def export_to_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe de Datos", 0)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col_name in enumerate(df.columns):
            hdr_cells[i].text = str(col_name)
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)
        buffer = BytesIO()
        doc.save(buffer)
        st.download_button("Descargar Word", buffer.getvalue(), file_name="informe.docx")
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

def panel_admin():
    st.title("Panel de Control - Administrador")
    st.success(f"Bienvenido administrador {st.session_state.username}")

    uploaded_file = st.file_uploader("Subir archivo CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

        st.subheader("Análisis Estadístico")
        st.write(df.describe())

        st.subheader("Gráficos Interactivos")
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            st.plotly_chart(px.line(numeric_df))
            st.plotly_chart(px.box(numeric_df))
        except Exception as e:
            st.error(f"Error al generar gráficos: {e}")

        st.subheader("Mapa de Correlación")
        try:
            fig = px.imshow(numeric_df.corr(), text_auto=True)
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Error en el mapa de correlación: {e}")

        st.subheader("Exportar Informe")
        export_to_pdf(df)
        export_to_word(df)

def main():
    if st.session_state.auth:
        st.sidebar.button("Cerrar sesión", on_click=logout)
        if st.session_state.role == "admin":
            panel_admin()
        else:
            st.warning("No tienes permisos para ver esta sección.")
    else:
        login()

if __name__ == "__main__":
    main()
    
