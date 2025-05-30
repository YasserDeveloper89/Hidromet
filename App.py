import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- Configuración de la Página ---
st.set_page_config(
    page_title="App Hidrometeorológica Avanzada",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Autenticación -----------------
USUARIOS = {
    "admin": "admin123",
    "tecnico": "tecnico123"
}

# ----------------- Login -----------------
def login():
    st.title("🔐 Acceso a la Plataforma")
    st.markdown("---")

    col_login_img, col_login_form = st.columns([1, 1])

    with col_login_img:
        st.image("https://images.unsplash.com/photo-1549740449-74e2d3b2c6a2?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                 caption="Monitoreo Inteligente del Clima", use_container_width=True) # ¡ACTUALIZADO AQUÍ!
        st.markdown("<p style='text-align: center; font-style: italic; color: grey;'>Una aplicación moderna para el análisis hidrometeorológico.</p>", unsafe_allow_html=True)


    with col_login_form:
        st.header("Por favor, inicia sesión")
        usuario = st.text_input("Usuario", help="Introduce tu nombre de usuario.")
        contraseña = st.text_input("Contraseña", type="password", help="Introduce tu contraseña.")
        
        if st.button("🚪 Iniciar sesión", use_container_width=True):
            if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.success(f"✅ ¡Bienvenido, {usuario}! Redirigiendo al panel...")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos. Inténtalo de nuevo.")

# ----------------- Logout -----------------
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.df_cargado = None
    st.rerun()

# ----------------- Generar PDF -----------------
def generar_pdf(df_to_export):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Datos Hidrometeorológicos", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, txt="Resumen del DataFrame:", ln=True)
    pdf.set_font("Arial", '', 10)
    for col in df_to_export.columns:
        pdf.cell(0, 7, txt=f"- {col}: {df_to_export[col].dtype}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Datos Detallados:", ln=True, align="C")
    pdf.ln(5)

    df_str = df_to_export.astype(str)

    num_cols_pdf = len(df_str.columns)
    if df_str.index.name is not None:
        num_cols_pdf += 1

    col_width = pdf.w / (num_cols_pdf + 1)

    pdf.set_font("Arial", 'B', 10)
    if df_str.index.name is not None:
        pdf.cell(col_width, 10, str(df_str.index.name if df_str.index.name else "Índice"), border=1)
    for col in df_str.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()

    pdf.set_font("Arial", '', 8)
    for index, row in df_str.iterrows():
        if isinstance(index, pd.Timestamp):
            pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d')), border=1)
        else:
            pdf.cell(col_width, 10, str(index), border=1)

        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    buffer = BytesIO()
    pdf.output(buffer, 'S')
    pdf_data = buffer.getvalue()
    return pdf_data

# ----------------- Generar Word -----------------
def generar_word(df_to_export):
    doc = Document()
    doc.add_heading("Reporte de Datos Hidrometeorológicos", 0)
    doc.add_paragraph(f"Fecha del Reporte: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    doc.add_page_break()

    doc.add_heading("Resumen de Datos", level=1)
    doc.add_paragraph(f"Número de filas: {len(df_to_export)}")
    doc.add_paragraph(f"Número de columnas: {len(df_to_export.columns)}")
    doc.add_paragraph("Tipos de datos por columna:")
    for col, dtype in df_to_export.dtypes.items():
        doc.add_paragraph(f"- {col}: {dtype}")
    doc.add_page_break()

    doc.add_heading("Datos Detallados", level=1)
    table = doc.add_table(rows=1, cols=len(df_to_export.columns) + (1 if df_to_export.index.name else 0))
    table.style = 'Table Grid'

    hdr_cells = table.rows[0].cells
    idx = 0
    if df_to_export.index.name:
        hdr_cells[idx].text = df_to_export.index.name if df_to_export.index.name else "Índice"
        idx += 1
    for i, col in enumerate(df_to_export.columns):
        hdr_cells[idx + i].text = col

    for index, row in df_to_export.iterrows():
        row_cells = table.add_row().cells
        idx = 0
        if df_to_export.index.name:
            if isinstance(index, pd.Timestamp):
                row_cells[idx].text = str(index.strftime('%Y-%m-%d'))
            else:
                row_cells[idx].text = str(index)
            idx += 1
        for i, col_name in enumerate(df_to_export.columns):
            row_cells[idx + i].text = str(row[col_name])
            
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ----------------- Panel de Administración -----------------
def admin_panel():
    st.sidebar.title(f"👋 Hola, {st.session_state.usuario}!")
    st.sidebar.button("Cerrar Sesión", on_click=logout, type="secondary", use_container_width=True)
    st.sidebar.markdown("---")

    st.title("💡 Dashboard Hidrometeorológico Interactivo")
    st.markdown("Una plataforma moderna para el análisis y visualización de datos climáticos.")
    st.markdown("---")

    tab_carga, tab_analisis, tab_exportacion = st.tabs(["📂 Cargar Datos", "📊 Análisis y Visualización", "📤 Exportar Reportes"])

    with tab_carga:
        st.header("Sube tus Datos CSV")
        st.info("Aquí puedes cargar tus archivos de datos hidrometeorológicos en formato CSV.")
        
        uploaded_file = st.file_uploader("Arrastra y suelta tu archivo CSV aquí o haz clic para buscarlo", type=["csv"],
                                         help="Asegúrate de que tu archivo CSV esté bien formateado.")

        if uploaded_file is None:
            st.session_state.df_cargado = None
            st.warning("Aún no hay datos cargados. Por favor, sube un archivo CSV para empezar a analizar.")
        else:
            with st.spinner("Cargando y procesando datos...
        
