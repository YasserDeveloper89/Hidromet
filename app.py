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

# --- Configurar la página ---
st.set_page_config(page_title="HydroClima PRO", layout="wide")

# --- Credenciales ---
USERS = {
    "admin": "admin123",
    "tecnico": "tecnico123",
    "cliente": "cliente123"
}

# --- Manejo de Sesiones ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- Función de Login ---
def login():
    st.title("🔐 Iniciar sesión en HydroClima PRO")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Bienvenido, {username}")
        else:
            st.error("Credenciales incorrectas")

# --- Función de Logout ---
def logout():
    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# --- Función para exportar Word ---
def export_word(df):
    doc = Document()
    doc.add_heading("Informe de Datos Hidrometeorológicos", 0)
    t = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = t.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for index, row in df.iterrows():
        row_cells = t.add_row().cells
        for i, item in enumerate(row):
            row_cells[i].text = str(item)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">📥 Descargar Informe Word</a>'
    st.markdown(href, unsafe_allow_html=True)

# --- Función para exportar PDF ---
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=True, align='C')
    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i] if isinstance(x, (int, float, str))])
        pdf.multi_cell(0, 10, txt=row)
    pdf_output = "informe.pdf"
    pdf.output(pdf_output)
    with open(pdf_output, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe.pdf">📥 Descargar Informe PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# --- Funciones Admin ---
def admin_panel():
    st.title("🧭 Panel de Control del Administrador")
    st.markdown("---")
    df = cargar_datos()
    if df is not None:
        st.subheader("📊 Vista previa de datos")
        st.dataframe(df, use_container_width=True)

        # Funcionalidad 1: Estadísticas básicas
        st.subheader("📌 Estadísticas generales")
        st.write(df.describe())

        # Funcionalidad 2: Gráficos interactivos
        st.subheader("📈 Gráficos interactivos")
        col = st.selectbox("Selecciona columna para gráfico de líneas", df.select_dtypes(include=[np.number]).columns)
        st.plotly_chart(px.line(df, y=col), use_container_width=True)

        # Funcionalidad 3: Mapa de correlación
        st.subheader("🧩 Mapa de correlación")
        numeric_df = df.select_dtypes(include=[np.number])
        fig_corr = px.imshow(numeric_df.corr(), text_auto=True, aspect="auto")
        st.plotly_chart(fig_corr, use_container_width=True)

        # Funcionalidad 4: Exportar a Word
        st.subheader("📤 Exportar informe")
        export_word(df)

        # Funcionalidad 5: Exportar a PDF
        export_pdf(df)

        # AÑADIR aquí más funcionalidades (6 a 15)
        st.markdown("---")
        st.info("✔️ Aún puedes añadir 10 herramientas más aquí según lo necesites")

# --- Cargar archivo CSV ---
def cargar_datos():
    archivo = st.file_uploader("📂 Carga tu archivo CSV de mediciones", type=["csv"])
    if archivo is not None:
        try:
            df = pd.read_csv(archivo)
            return df
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    return None

# --- MAIN APP ---
if not st.session_state.logged_in:
    login()
else:
    logout()
    st.sidebar.success(f"Sesión iniciada como {st.session_state.username}")

    if st.session_state.username == "admin":
        admin_panel()
    else:
        st.warning("Usuario válido pero aún no se ha definido una vista personalizada para este rol.")
