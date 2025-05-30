import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from docx import Document
from io import BytesIO

# --------------------
# CONFIGURACIÓN INICIAL
# --------------------
st.set_page_config(page_title="Panel Administrador", layout="wide")

USERS = {"admin": "admin123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --------------------
# FUNCIONES UTILITARIAS
# --------------------
def export_to_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        col_width = pdf.w / (len(df.columns) + 1)

        for col in df.columns:
            pdf.cell(col_width, 10, col, 1)
        pdf.ln()

        for index, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 10, str(item), 1)
            pdf.ln()

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")
        return None

def export_to_word(df):
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

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error al generar Word: {e}")
        return None

# --------------------
# PANEL DE ADMINISTRADOR
# --------------------
def admin_panel():
    st.title("📊 Panel de Control del Administrador")
    
    uploaded_file = st.file_uploader("📤 Cargar archivo CSV", type=["csv"])
    if uploaded_file is not None:
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

            pdf_buffer = export_to_pdf(df)
            if pdf_buffer:
                st.download_button("📄 Descargar PDF", data=pdf_buffer, file_name="informe.pdf", mime="application/pdf")

            word_buffer = export_to_word(df)
            if word_buffer:
                st.download_button("📝 Descargar Word", data=word_buffer, file_name="informe.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        st.info("Por favor cargue un archivo para acceder a las herramientas.")

    st.markdown("---")
    if st.button("🚪 Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""

# --------------------
# LOGIN
# --------------------
def login():
    st.title("Acceso al Sistema")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")

    if submit:
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Bienvenido, {username}")
        else:
            st.error("Credenciales inválidas")

# --------------------
# MAIN
# --------------------
def main():
    if st.session_state.logged_in:
        admin_panel()
    else:
        login()

main()
