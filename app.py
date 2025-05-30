import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from docx import Document
from io import BytesIO

# --- Configuración ---
st.set_page_config("Panel Hidromet", layout="wide")

# --- Usuarios válidos ---
USERS = {"admin": "admin123"}

# --- Estado de sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Exportar a PDF ---
def export_to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)

    for col in df.columns:
        pdf.cell(col_width, 10, col, 1)
    pdf.ln()

    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(item), 1)
        pdf.ln()

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Exportar a Word ---
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
    return buffer

# --- Panel del administrador ---
def admin_panel():
    st.title("📊 Panel de Control del Administrador")

    uploaded_file = st.file_uploader("📤 Cargar archivo CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo cargado correctamente ✅")

            st.subheader("🔍 Vista previa de datos")
            st.dataframe(df)

            st.subheader("📈 Estadísticas básicas")
            st.write(df.describe())

            st.subheader("📌 Gráfico de correlación")
            numeric_df = df.select_dtypes(include='number')
            if not numeric_df.empty:
                fig_corr = px.imshow(numeric_df.corr(), text_auto=True, aspect="auto")
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("No hay suficientes datos numéricos para graficar.")

            pdf = export_to_pdf(df)
            st.download_button("📄 Descargar PDF", data=pdf, file_name="informe.pdf", mime="application/pdf")

            word = export_to_word(df)
            st.download_button("📝 Descargar Word", data=word, file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
    else:
        st.info("Suba un archivo CSV para comenzar.")

    st.markdown("---")
    if st.button("🚪 Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""

# --- Formulario de login ---
def login_form():
    st.title("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Credenciales incorrectas")

# --- Main ---
def main():
    if st.session_state.logged_in:
        admin_panel()
    else:
        login_form()

main()
