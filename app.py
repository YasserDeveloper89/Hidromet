import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime

# --- Configuración inicial ---
st.set_page_config(page_title="Panel Hidromet", layout="wide")

# --- Base de usuarios ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tec456", "role": "tecnico"}
}

# --- Gestión de sesión ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# --- Login ---
def login():
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_btn = st.button("Iniciar sesión")

    if login_btn:
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.success(f"Login exitoso. Bienvenido, {username}")
        else:
            st.error("Credenciales inválidas")

# --- Logout ---
def logout():
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

# --- Función principal ---
def main():
    if not st.session_state.authenticated:
        login()
    else:
        st.sidebar.title(f"Panel de {st.session_state.role.capitalize()}")
        logout()

        st.title("Panel de Control Hidromet")
        file = st.file_uploader("Subir archivo CSV", type="csv")
        if file is not None:
            try:
                df = pd.read_csv(file)
                st.success("Archivo cargado exitosamente.")
                st.write(df.head())

                # --- Herramientas de administrador ---
                if st.session_state.role == "admin":
                    admin_tools(df)

            except Exception as e:
                st.error(f"Error al cargar el archivo: {e}")
        else:
            st.warning("Por favor cargue un archivo para acceder a las herramientas.")

# --- Herramientas de administrador ---
def admin_tools(df):
    st.subheader("📊 Análisis de Datos para Administrador")

    # Herramienta 1: Gráfico de líneas
    st.write("### Tendencia temporal")
    column = st.selectbox("Seleccione la columna para graficar", df.select_dtypes(include=np.number).columns)
    st.line_chart(df[column])

    # Herramienta 2: Estadísticas
    st.write("### Estadísticas básicas")
    st.write(df.describe())

    # Herramienta 3: Correlación
    st.write("### Mapa de correlación")
    num_df = df.select_dtypes(include=[np.number])
    if not num_df.empty:
        fig_corr = px.imshow(num_df.corr(), text_auto=True, aspect="auto")
        st.plotly_chart(fig_corr)
    else:
        st.warning("No hay columnas numéricas suficientes para generar el mapa de correlación.")

    # Herramienta 4: Exportar a PDF
    if st.button("📥 Exportar informe PDF"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe de Datos Hidromet", ln=1, align="C")
            for col in df.columns:
                pdf.cell(200, 10, txt=col + ": " + str(df[col].iloc[0]), ln=1)
            buffer = BytesIO()
            pdf.output(buffer)
            st.download_button(label="Descargar PDF", data=buffer.getvalue(), file_name="informe.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

    # Herramienta 5: Exportar a Word
    if st.button("📥 Exportar informe Word"):
        try:
            doc = Document()
            doc.add_heading("Informe de Datos Hidromet", 0)
            table = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = str(col)
            for index, row in df.iterrows():
                row_cells = table.add_row().cells
                for i, val in enumerate(row):
                    row_cells[i].text = str(val)
            buffer = BytesIO()
            doc.save(buffer)
            st.download_button(label="Descargar Word", data=buffer.getvalue(), file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.error(f"Error al generar Word: {e}")

if __name__ == '__main__':
    main()
            
