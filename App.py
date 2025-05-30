import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document

st.set_page_config(page_title="Hidromet", layout="wide")

# ----------------- Estado de sesión -----------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

USUARIOS = {"admin": "admin123"}

# ----------------- Función Login -----------------
def login():
    st.title("🔐 Inicio de sesión")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    login_btn = st.button("Iniciar sesión")

    if login_btn:
        if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.experimental_set_query_params(logged="true")
        else:
            st.error("❌ Usuario o contraseña incorrectos")

# ----------------- Función Logout -----------------
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.experimental_set_query_params()
    st.experimental_rerun()

# ----------------- Exportar PDF -----------------
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = 10

    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln()

    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln()

    output = BytesIO()
    pdf.output(output, 'F')
    return output.getvalue()

# ----------------- Exportar Word -----------------
def generar_word(df):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells

    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)

    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, item in enumerate(row):
            row_cells[i].text = str(item)

    output = BytesIO()
    doc.save(output)
    return output.getvalue()

# ----------------- Panel Admin -----------------
def admin_panel():
    st.sidebar.success(f"👋 Bienvenido {st.session_state.usuario}")
    if st.sidebar.button("Cerrar sesión"):
        logout()

    st.title("📊 Panel Administrativo Hidromet")
    file = st.file_uploader("📁 Cargar archivo CSV", type="csv")

    if file:
        df = pd.read_csv(file)
        st.dataframe(df)

        st.subheader("📈 Visualización de datos")

        col1, col2 = st.columns(2)

        with col1:
            num_cols = df.select_dtypes(include='number').columns.tolist()
            if num_cols:
                col_selected = st.selectbox("Selecciona una columna numérica", num_cols)
                fig1, ax1 = plt.subplots()
                sns.histplot(df[col_selected], kde=True, ax=ax1)
                st.pyplot(fig1)
            else:
                st.warning("⚠️ No hay columnas numéricas.")

        with col2:
            try:
                fig2 = px.imshow(df.select_dtypes(include='number').corr(), text_auto=True)
                st.plotly_chart(fig2)
            except Exception as e:
                st.warning(f"No se pudo generar el mapa de correlación: {e}")

        st.subheader("📄 Exportar Reportes")
        col3, col4 = st.columns(2)

        with col3:
            try:
                pdf_data = generar_pdf(df)
                b64_pdf = base64.b64encode(pdf_data).decode()
                href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="reporte.pdf">📄 Descargar PDF</a>'
                st.markdown(href_pdf, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error exportando PDF: {e}")

        with col4:
            try:
                word_data = generar_word(df)
                b64_word = base64.b64encode(word_data).decode()
                href_word = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="reporte.docx">📄 Descargar Word</a>'
                st.markdown(href_word, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error exportando Word: {e}")

        st.subheader("🛠️ Herramientas adicionales")

        if df.isnull().values.any():
            st.write("🔍 Filas con valores nulos")
            st.dataframe(df[df.isnull().any(axis=1)])

        st.write("📊 Estadísticas generales")
        st.dataframe(df.describe())

        st.write("📌 Conteo de valores categóricos")
        for col in df.select_dtypes(include='object').columns:
            st.write(f"Columna: `{col}`")
            st.dataframe(df[col].value_counts())

# ----------------- Main -----------------
def main():
    if st.session_state.autenticado:
        admin_panel()
    else:
        login()

main()
