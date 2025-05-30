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

st.set_page_config(page_title="Hidromet Admin PRO", layout="wide", page_icon="📊")

# --- Utilidades ---
def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Reporte de Datos", ln=True, align='C')
        pdf.ln(10)

        col_names = df.columns.tolist()
        pdf.cell(200, 10, txt=" | ".join(col_names), ln=True)

        for _, row in df.iterrows():
            line = " | ".join(str(x) for x in row)
            pdf.cell(200, 10, txt=line, ln=True)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")


def export_word(df):
    try:
        doc = Document()
        doc.add_heading('Reporte de Datos', 0)

        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, column in enumerate(df.columns):
            hdr_cells[i].text = str(column)

        for index, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, cell in enumerate(row):
                row_cells[i].text = str(cell)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

# --- Simulación de usuarios ---
USUARIOS = {
    "admin": "admin123",
    "tecnico": "tec456"
}

if "login" not in st.session_state:
    st.session_state.login = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login():
    st.title("Inicio de sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USUARIOS and USUARIOS[username] == password:
            st.session_state.login = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas")

def logout():
    if st.button("Cerrar sesión"):
        st.session_state.login = False
        st.session_state.username = ""
        st.experimental_rerun()

def admin_panel():
    st.sidebar.header("Panel Administrador")
    logout()
    st.title("Panel de Control - Administrador")

    archivo = st.file_uploader("Sube un archivo CSV", type="csv")
    if archivo is not None:
        df = pd.read_csv(archivo)

        st.subheader("1. Vista previa de los datos")
        st.dataframe(df)

        st.subheader("2. Estadísticas descriptivas")
        st.write(df.describe())

        st.subheader("3. Gráficos interactivos")
        numeric_df = df.select_dtypes(include='number')
        if not numeric_df.empty:
            st.plotly_chart(px.line(numeric_df))

        st.subheader("4. Histograma")
        col = st.selectbox("Selecciona columna para histograma", numeric_df.columns)
        st.plotly_chart(px.histogram(df, x=col))

        st.subheader("5. Mapa de correlación")
        fig_corr = px.imshow(numeric_df.corr(), text_auto=True, aspect="auto")
        st.plotly_chart(fig_corr)

        st.subheader("6. Exportar informe")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Exportar a Word"):
                docx_file = export_word(df)
                st.download_button("Descargar Word", data=docx_file, file_name="informe.docx")
        with col2:
            if st.button("📑 Exportar a PDF"):
                pdf_file = export_pdf(df)
                st.download_button("Descargar PDF", data=pdf_file, file_name="informe.pdf")

        st.subheader("7. Filtros avanzados")
        filtro_col = st.selectbox("Filtrar por columna", df.columns)
        valores = df[filtro_col].unique()
        seleccion = st.multiselect("Selecciona valores", valores)
        if seleccion:
            st.dataframe(df[df[filtro_col].isin(seleccion)])

        st.subheader("8. Detección de valores nulos")
        st.dataframe(df.isnull().sum())

        st.subheader("9. Gráfico de cajas")
        st.plotly_chart(px.box(df, y=col))

        st.subheader("10. Exportar CSV limpio")
        st.download_button("Descargar CSV", data=df.to_csv(index=False), file_name="datos_limpios.csv")

        st.subheader("11. Matriz de dispersión")
        st.plotly_chart(px.scatter_matrix(numeric_df))

        st.subheader("12. Valores máximos/mínimos")
        st.write("Máximos")
        st.write(df.max())
        st.write("Mínimos")
        st.write(df.min())

        st.subheader("13. Conexión a sensores [SIMULADO]")
        st.info("⏳ Conectando a sensores en tiempo real... [Simulado]")

        st.subheader("14. Guardar configuración")
        nombre = st.text_input("Nombre del archivo de configuración")
        if st.button("Guardar configuración"):
            st.success(f"Configuración '{nombre}' guardada con éxito [Simulado]")

        st.subheader("15. Monitor en tiempo real")
        st.line_chart(numeric_df.head(100))

    else:
        st.info("Por favor, sube un archivo CSV para empezar")

# --- App Main ---
if not st.session_state.login:
    login()
else:
    if st.session_state.username == "admin":
        admin_panel()
    else:
        st.title(f"Bienvenido, {st.session_state.username}")
        st.info("Este usuario aún no tiene funciones avanzadas en esta versión.")
        
