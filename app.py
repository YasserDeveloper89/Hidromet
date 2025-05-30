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

# ----------------------- CONFIG -----------------------
st.set_page_config(page_title="Panel Administrador", layout="wide")

# ----------------------- SESSION INIT -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ----------------------- LOGIN FUNCTION -----------------------
def login():
    st.title("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_btn = st.button("Iniciar sesión")

    if login_btn:
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  # Recarga inmediatamente
        else:
            st.error("Credenciales inválidas")

# ----------------------- LOGOUT FUNCTION -----------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Se ha cerrado la sesión correctamente")
    st.rerun()

# ----------------------- PDF EXPORT FUNCTION -----------------------
def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
        pdf.ln(10)
        col_names = ", ".join(df.columns)
        pdf.multi_cell(0, 10, col_names)
        for i, row in df.iterrows():
            line = ", ".join(str(val) for val in row)
            pdf.multi_cell(0, 10, line)
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        b64 = base64.b64encode(pdf_output.read()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

# ----------------------- WORD EXPORT FUNCTION -----------------------
def export_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe de Datos", 0)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = col
        for index, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, cell in enumerate(row):
                row_cells[i].text = str(cell)
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

# ----------------------- ADMIN PANEL -----------------------
def admin_panel():
    st.title("Panel de Administración")
    st.sidebar.button("Cerrar sesión", on_click=logout)

    uploaded_file = st.file_uploader("Suba su archivo CSV de mediciones", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo cargado con éxito")
            st.subheader("Vista de Datos")
            st.dataframe(df)

            st.subheader("Exportaciones")
            col1, col2 = st.columns(2)
            with col1:
                export_pdf(df)
            with col2:
                export_word(df)

            st.subheader("Gráficos Interactivos")
            num_df = df.select_dtypes(include=[np.number])
            if not num_df.empty:
                fig_corr = px.imshow(num_df.corr(), text_auto=True, aspect="auto", title="Mapa de Correlación")
                st.plotly_chart(fig_corr, use_container_width=True)

                for col in num_df.columns:
                    st.plotly_chart(px.line(num_df, y=col, title=f"Tendencia de {col}"), use_container_width=True)
            else:
                st.warning("No hay columnas numéricas para visualizar")

            st.subheader("Estadísticas Descriptivas")
            st.write(num_df.describe())

            st.subheader("Histograma")
            col = st.selectbox("Selecciona una columna", num_df.columns)
            st.plotly_chart(px.histogram(df, x=col), use_container_width=True)

            # Añadir 10 herramientas más aquí...
            # Ej: clustering, PCA, detección de outliers, dashboard por fecha, etc.

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.info("Por favor cargue un archivo para acceder a las herramientas")

# ----------------------- MAIN -----------------------
def main():
    if st.session_state.logged_in:
        admin_panel()
    else:
        login()

if __name__ == "__main__":
    main()
    
