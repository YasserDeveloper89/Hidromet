# app.py
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

# --------------------- LOGIN Y SESION ---------------------
USERS = {"admin": "admin123"}  # Usuario fijo para pruebas

def login():
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Credenciales inválidas")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

# -------------------- EXPORTACION PDF Y WORD --------------------
def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
        for i in range(len(df)):
            row = ', '.join([str(x) for x in df.iloc[i]])
            pdf.multi_cell(0, 10, row)
        output = BytesIO()
        pdf.output(output)
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe.pdf">Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

def export_word(df):
    try:
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
        output = BytesIO()
        doc.save(output)
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

# ---------------------- FUNCIONES AVANZADAS ----------------------
def admin_panel():
    st.title("Panel de Control - Administrador")
    st.button("Cerrar sesión", on_click=logout)

    uploaded_file = st.file_uploader("Cargar archivo CSV", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo cargado correctamente")

            # Visualización básica
            st.subheader("Vista previa de datos")
            st.dataframe(df)

            # Estadísticas
            st.subheader("Estadísticas descriptivas")
            st.write(df.describe())

            # Exportar
            export_pdf(df)
            export_word(df)

            # Gráficos
            st.subheader("Gráficos interactivos")
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                st.plotly_chart(px.imshow(numeric_df.corr(), text_auto=True, title="Mapa de Correlación"))
                for col in numeric_df.columns:
                    st.plotly_chart(px.histogram(numeric_df, x=col))
                    st.plotly_chart(px.line(numeric_df, y=col))
            else:
                st.warning("No hay columnas numéricas para graficar.")

            # Herramientas adicionales
            st.subheader("Otras herramientas")
            st.write("- Detección de valores nulos")
            st.dataframe(df.isnull().sum())

            st.write("- Filtrado por columnas")
            column = st.selectbox("Selecciona una columna", df.columns)
            st.dataframe(df[column])

            st.write("- Top 10 valores máximos")
            st.dataframe(df.nlargest(10, column))

            st.write("- Búsqueda personalizada")
            query = st.text_input("Buscar valor")
            if query:
                mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
                st.dataframe(df[mask])

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.warning("Por favor cargue un archivo para acceder a las herramientas")

# ------------------------- MAIN -------------------------
def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""

    if st.session_state.authenticated:
        if st.session_state.username == "admin":
            admin_panel()
    else:
        login()

if __name__ == "__main__":
    main()
                
