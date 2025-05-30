import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime

# --- Autenticación ---
USERS = {
    "admin": "admin123",
    "tecnico": "tec123",
    "usuario": "user123"
}

def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        with st.form("login_form"):
            st.title("Inicio de sesión")
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar sesión")
        if submit:
            if username in USERS and USERS[username] == password:
                st.session_state.username = username
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Credenciales inválidas")
    else:
        st.success(f"Login exitoso. Bienvenido, {st.session_state.username}")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.experimental_rerun()

def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=True, align='C')
        for i in range(len(df)):
            row = ', '.join([str(x) for x in df.iloc[i]])
            pdf.multi_cell(0, 10, row)
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        st.download_button("Descargar PDF", data=pdf_output.getvalue(), file_name="informe.pdf")
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

def export_word(df):
    try:
        doc = Document()
        doc.add_heading('Informe de Datos Hidrometeorológicos', 0)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col_name in enumerate(df.columns):
            hdr_cells[i].text = str(col_name)
        for i in range(len(df)):
            row_cells = table.add_row().cells
            for j, val in enumerate(df.iloc[i]):
                row_cells[j].text = str(val)
        buffer = BytesIO()
        doc.save(buffer)
        st.download_button("Descargar Word", data=buffer.getvalue(), file_name="informe.docx")
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

def admin_panel():
    st.title("Panel de Administración")
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo cargado correctamente")

            st.subheader("Vista previa de los datos")
            st.dataframe(df)

            st.subheader("Gráficos Interactivos")
            numeric_cols = df.select_dtypes(include=np.number).columns
            if len(numeric_cols) >= 2:
                fig1 = px.line(df, x=numeric_cols[0], y=numeric_cols[1])
                st.plotly_chart(fig1)

                fig2 = px.histogram(df, x=numeric_cols[0])
                st.plotly_chart(fig2)

                fig3 = px.scatter_matrix(df[numeric_cols])
                st.plotly_chart(fig3)

                fig4 = px.imshow(df[numeric_cols].corr())
                st.plotly_chart(fig4)

            export_pdf(df)
            export_word(df)

            # Más herramientas profesionales se pueden incluir aquí...
            st.subheader("Análisis estadístico")
            st.write(df.describe())

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        st.warning("Por favor cargue un archivo para acceder a las herramientas")

def main():
    login()
    if st.session_state.get("authenticated"):
        if st.button("Cerrar sesión"):
            logout()
        if st.session_state.username == "admin":
            admin_panel()
        else:
            st.info("Panel para otros usuarios en desarrollo")

if __name__ == "__main__":
    main()
    
