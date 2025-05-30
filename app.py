import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from docx import Document
from fpdf import FPDF
import base64

# --- Configuración de página ---
st.set_page_config(page_title="HydroClimaPRO", layout="wide")

# --- Simulación de base de usuarios ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tec456", "role": "tecnico"},
    "usuario": {"password": "user789", "role": "usuario"}
}

# --- Funciones auxiliares ---
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Sesión cerrada correctamente.")
    st.experimental_set_query_params()


def download_button(buffer, filename, mime):
    b64 = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:{mime};base64,{b64}" download="{filename}" class="download-btn">Descargar {filename}</a>'
    return href


def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Reporte de Datos", ln=True, align='C')
        pdf.ln(10)
        col_width = pdf.w / (len(df.columns) + 1)
        row_height = 8

        for col in df.columns:
            pdf.cell(col_width, row_height, txt=str(col), border=1)
        pdf.ln(row_height)

        for _, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, row_height, txt=str(item), border=1)
            pdf.ln(row_height)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return download_button(buffer, "reporte.pdf", "application/pdf")
    except Exception as e:
        return f"<p style='color:red;'>Error al generar PDF: {e}</p>"


def export_word(df):
    try:
        doc = Document()
        doc.add_heading('Reporte de Datos', 0)
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
        buffer.seek(0)
        return download_button(buffer, "reporte.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        return f"<p style='color:red;'>Error al generar Word: {e}</p>"


def admin_panel(df):
    st.title("Panel de Administración 🛠️")
    st.markdown("---")

    st.subheader("📊 Visualización de Datos")
    st.dataframe(df)

    st.subheader("📈 Gráficos Interactivos")
    st.plotly_chart(px.line(df))

    st.subheader("📌 Mapa de correlación")
    try:
        fig_corr = px.imshow(df.corr(numeric_only=True), text_auto=True, aspect="auto")
        st.plotly_chart(fig_corr)
    except Exception as e:
        st.error(f"Error al generar mapa de correlación: {e}")

    st.subheader("📥 Exportar Reportes")
    st.markdown(export_pdf(df), unsafe_allow_html=True)
    st.markdown(export_word(df), unsafe_allow_html=True)

    st.subheader("🔌 Conexión con sensores")
    st.success("Conectado al sensor X - datos sincronizados")


def login():
    st.title("🔐 Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_btn = st.button("Iniciar Sesión")

    if login_btn:
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            st.rerun()
        else:
            st.error("Credenciales inválidas")


# --- App Principal ---
if "logged_in" not in st.session_state:
    login()
else:
    st.sidebar.title("Menú")
    st.sidebar.write(f"👤 Usuario: {st.session_state['username']}")
    if st.sidebar.button("Cerrar Sesión"):
        logout()
        st.rerun()

    uploaded_file = st.sidebar.file_uploader("Subir archivo CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if st.session_state["role"] == "admin":
                admin_panel(df)
            else:
                st.warning("Este rol aún no tiene acceso completo. Inicia sesión como admin.")
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        st.warning("Por favor, sube un archivo CSV para comenzar.")
    
