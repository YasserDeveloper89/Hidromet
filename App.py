import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import base64
from io import BytesIO
from docx import Document
from fpdf import FPDF

# ------------------ CONFIGURACIÓN ------------------ #
st.set_page_config(page_title="Panel Hidromet", layout="wide")

USUARIOS = {"admin": "admin123"}

# ------------------ INICIALIZACIÓN SESIÓN ------------------ #
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "logout" not in st.session_state:
    st.session_state.logout = False

# ------------------ LOGIN ------------------ #
def login():
    st.title("🔐 Login de Administrador")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
        else:
            st.error("❌ Credenciales incorrectas")

# ------------------ CERRAR SESIÓN ------------------ #
def cerrar_sesion():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.logout = True
    st.experimental_set_query_params()  # Limpia la URL

# ------------------ EXPORTAR PDF ------------------ #
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for i, col in enumerate(df.columns):
        pdf.cell(40, 10, col, 1)
    pdf.ln()
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(40, 10, str(item), 1)
        pdf.ln()
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

# ------------------ EXPORTAR WORD ------------------ #
def generar_word(df):
    doc = Document()
    doc.add_heading("Informe de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, item in enumerate(row):
            row_cells[i].text = str(item)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ------------------ PANEL ADMINISTRADOR ------------------ #
def admin_panel():
    st.sidebar.header(f"👤 Usuario: {st.session_state.usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        cerrar_sesion()
        st.rerun()

    st.title("📊 Panel Administrativo Hidromet")
    file = st.file_uploader("📂 Carga tu archivo CSV", type=["csv"])
    
    if file:
        df = pd.read_csv(file)
        st.success("✅ Archivo cargado correctamente")
        st.dataframe(df)

        # Herramientas
        st.subheader("📈 Visualización de Datos")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Histograma")
            col = st.selectbox("Selecciona columna numérica", df.select_dtypes(include='number').columns)
            fig, ax = plt.subplots()
            sns.histplot(df[col], kde=True, ax=ax)
            st.pyplot(fig)

        with col2:
            st.markdown("#### Mapa de Correlación")
            corr = df.select_dtypes(include='number').corr()
            fig_corr = px.imshow(corr, text_auto=True)
            st.plotly_chart(fig_corr)

        st.subheader("📄 Exportación de Informes")
        col3, col4 = st.columns(2)

        with col3:
            pdf_data = generar_pdf(df)
            b64_pdf = base64.b64encode(pdf_data).decode()
            href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="reporte.pdf">📄 Descargar PDF</a>'
            st.markdown(href_pdf, unsafe_allow_html=True)

        with col4:
            word_data = generar_word(df)
            b64_word = base64.b64encode(word_data).decode()
            href_word = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="reporte.docx">📄 Descargar Word</a>'
            st.markdown(href_word, unsafe_allow_html=True)

        # Más herramientas
        st.subheader("📌 Otras Herramientas")
        st.write("- Filtrar por valores nulos")
        st.dataframe(df[df.isnull().any(axis=1)])
        st.write("- Descripción estadística")
        st.dataframe(df.describe())
        st.write("- Conteo de valores por categoría")
        for col in df.select_dtypes(include='object').columns:
            st.write(f"📊 {col}")
            st.dataframe(df[col].value_counts())

# ------------------ MAIN ------------------ #
def main():
    if st.session_state.autenticado:
        admin_panel()
    else:
        login()

main()
