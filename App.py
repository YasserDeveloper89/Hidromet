import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document
from docx.shared import Inches # Para ajustar tamaños en Word
from docx.enum.text import WD_ALIGN_PARAGRAPH # Para alinear texto en Word


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
        # --- USANDO IMAGEN LOCAL! ---
        # Asegúrate de que 'login_background.jpg' esté en la misma carpeta que App.py
        st.image("login_background.jpg",
                 caption="Monitoreo Inteligente del Clima", use_container_width=True)
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

# ----------------- Generar PDF (MEJORADA) -----------------
def generar_pdf(df_to_export):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Datos Hidrometeorológicos", ln=True, align="C")
    pdf.ln(10)

    # --- Sección de Resumen General ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="1. Resumen General del Conjunto de Datos", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, txt=f"  - Número total de filas: {len(df_to_export)}", ln=True)
    pdf.cell(0, 7, txt=f"  - Número total de columnas: {len(df_to_export.columns)}", ln=True)
    
    if isinstance(df_to_export.index, pd.DatetimeIndex):
        pdf.cell(0, 7, txt=f"  - Período de datos: {df_to_export.index.min().strftime('%Y-%m-%d')} a {df_to_export.index.max().strftime('%Y-%m-%d')}", ln=True)
    
    pdf.ln(5)

    # --- Sección de Resumen por Columna (Tipos de Datos y Valores Únicos) ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="2. Detalles de las Columnas", ln=True)
    pdf.set_font("Arial", '', 9) # Fuente más pequeña para detalles
    for col in df_to_export.columns:
        pdf.cell(0, 6, txt=f"  - '{col}':", ln=True)
        pdf.cell(0, 6, txt=f"    - Tipo de dato: {df_to_export[col].dtype}", ln=True)
        if df_to_export[col].dtype == 'object' or df_to_export[col].nunique() < 20: # Para columnas categóricas o con pocos valores únicos
            pdf.cell(0, 6, txt=f"    - Valores únicos: {df_to_export[col].nunique()}", ln=True)
        
        # Si es numérica, añadir estadísticas descriptivas
        if pd.api.types.is_numeric_dtype(df_to_export[col]):
            desc_stats = df_to_export[col].describe()
            pdf.cell(0, 6, txt=f"    - Media: {desc_stats['mean']:.2f}", ln=True)
            pdf.cell(0, 6, txt=f"    - Desviación Estándar: {desc_stats['std']:.2f}", ln=True)
            pdf.cell(0, 6, txt=f"    - Mínimo: {desc_stats['min']:.2f}", ln=True)
            pdf.cell(0, 6, txt=f"    - Máximo: {desc_stats['max']:.2f}", ln=True)
        pdf.ln(2) # Pequeño espacio entre columnas

    pdf.ln(5) # Espacio antes de la tabla

    # --- Sección de Datos Detallados (Tabla) ---
    pdf.add_page() # Nueva página para la tabla si es muy grande
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="3. Datos Detallados del Conjunto", ln=True, align="C")
    pdf.ln(5)

    df_str = df_to_export.astype(str)

    # Calcular ancho de columnas dinámicamente para la tabla
    num_cols_pdf = len(df_str.columns)
    has_index_name = df_str.index.name is not None and df_str.index.name != '' # Check if index has a meaningful name
    if has_index_name or isinstance(df_to_export.index, pd.DatetimeIndex): # Always show date index
        num_cols_pdf += 1 
        
    # Ancho aproximado de la página para la tabla, ajustado para evitar desbordamientos
    page_width = pdf.w - 2*pdf.l_margin
    col_width = page_width / num_cols_pdf
    
    # Si las columnas son muchas, ajustar el tamaño de fuente o dividir
    if num_cols_pdf > 6:
        pdf.set_font("Arial", 'B', 7) # Fuente más pequeña para encabezados
    else:
        pdf.set_font("Arial", 'B', 9)

    # Encabezados de la tabla
    if has_index_name:
        pdf.cell(col_width, 10, str(df_to_export.index.name), border=1, align='C')
    elif isinstance(df_to_export.index, pd.DatetimeIndex):
        pdf.cell(col_width, 10, "Fecha/Hora", border=1, align='C') # Generic name for datetime index
    
    for col in df_str.columns:
        pdf.cell(col_width, 10, str(col), border=1, align='C')
    pdf.ln()

    # Filas de datos
    if num_cols_pdf > 6:
        pdf.set_font("Arial", '', 6) # Fuente más pequeña para datos
    else:
        pdf.set_font("Arial", '', 7)

    for index, row in df_str.iterrows():
        # Valor del índice
        if has_index_name:
            if isinstance(index, pd.Timestamp):
                pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d %H:%M')), border=1)
            else:
                pdf.cell(col_width, 10, str(index), border=1)
        elif isinstance(df_to_export.index, pd.DatetimeIndex): # If index is datetime but no specific name
            pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d %H:%M')), border=1)
        
        # Valores de las columnas
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    buffer = BytesIO()
    pdf.output(buffer, 'S')
    pdf_data = buffer.getvalue()
    return pdf_data

# ----------------- Generar Word (MEJORADA) -----------------
