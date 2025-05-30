import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
import base64

# ---- Configuración de la página ----
st.set_page_config(page_title="HydroClima PRO", layout="wide", page_icon="💧")

# ---- Usuarios simulados ----
USUARIOS = {
    "admin": {"password": "admin123", "rol": "Administrador"},
    "tecnico": {"password": "tec456", "rol": "Técnico"},
    "visual": {"password": "vis789", "rol": "Visualizador"}
}

# ---- Variables de sesión ----
if "logueado" not in st.session_state:
    st.session_state.logueado = False
    st.session_state.usuario = ""
    st.session_state.rol = ""

# ---- Login ----
def login():
    with st.container():
        st.title("🔐 Iniciar sesión")
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Acceder"):
            if usuario in USUARIOS and USUARIOS[usuario]["password"] == password:
                st.session_state.logueado = True
                st.session_state.usuario = usuario
                st.session_state.rol = USUARIOS[usuario]["rol"]
                st.success(f"Bienvenido, {st.session_state.usuario.title()} ({st.session_state.rol})")
                st.experimental_rerun()
            else:
                st.error("Credenciales incorrectas")

# ---- Cierre de sesión ----
def logout():
    if st.sidebar.button("🔓 Cerrar sesión"):
        st.session_state.logueado = False
        st.session_state.usuario = ""
        st.session_state.rol = ""
        st.experimental_rerun()

# ---- Exportar PDF ----
def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
        pdf.ln(10)

        for i in range(len(df)):
            row = ', '.join([str(x) for x in df.iloc[i]])
            pdf.cell(200, 10, txt=row, ln=True, align="L")

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">📄 Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ocurrió un error al generar el PDF: {e}")

# ---- Exportar Word ----
def export_word(df):
    try:
        doc = Document()
        doc.add_heading('Informe de Datos', 0)
        t = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = t.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)

        for i in df.index:
            row_cells = t.add_row().cells
            for j, col in enumerate(df.columns):
                row_cells[j].text = str(df.at[i, col])

        bio = BytesIO()
        doc.save(bio)
        bio.seek(0)
        b64 = base64.b64encode(bio.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">📝 Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al exportar Word: {e}")

# ---- Función: Visualización de datos ----
def show_data(df):
    st.subheader("📊 Vista previa de datos")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Gráficos interactivos")
    col_x = st.selectbox("Selecciona eje X", df.columns)
    col_y = st.selectbox("Selecciona eje Y", df.columns)
    
    if pd.api.types.is_numeric_dtype(df[col_y]):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df[col_x], y=df[col_y], mode='lines+markers', 
            line=dict(color='cyan'), marker=dict(size=5)
        ))
        fig.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("La columna Y debe ser numérica")

# ---- Funciones estadísticas adicionales ----
def estadisticas_avanzadas(df):
    st.subheader("📌 Estadísticas adicionales")
    col = st.selectbox("Selecciona una columna", df.select_dtypes(include=np.number).columns)
    if col:
        st.write(f"Media: {df[col].mean():.2f}")
        st.write(f"Mediana: {df[col].median():.2f}")
        st.write(f"Desviación estándar: {df[col].std():.2f}")
        st.write(f"Mínimo: {df[col].min():.2f}")
        st.write(f"Máximo: {df[col].max():.2f}")

# ---- Panel de Administrador ----
def admin_panel(df):
    st.title("🛠️ Panel del Administrador")
    st.success("Tienes acceso total al sistema.")
    show_data(df)
    estadisticas_avanzadas(df)
    export_pdf(df)
    export_word(df)
    st.markdown("---")
    st.subheader("🔗 Conexión a sensores remotos")
    st.info("Simulación: Conexión establecida con sensores externos (API/Satelital)... [modo demo]")

# ---- Panel de Técnico ----
def tecnico_panel(df):
    st.title("🔧 Panel Técnico")
    show_data(df)
    estadisticas_avanzadas(df)
    export_pdf(df)
    export_word(df)

# ---- Panel de Visualizador ----
def visual_panel(df):
    st.title("👁️ Panel de Visualización")
    show_data(df)

# ---- MAIN APP ----
if not st.session_state.logueado:
    login()
else:
    logout()

    st.sidebar.title("📂 Cargar datos")
    file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])
    if file:
        try:
            df = pd.read_csv(file)
            rol = st.session_state.rol
            if rol == "Administrador":
                admin_panel(df)
            elif rol == "Técnico":
                tecnico_panel(df)
            elif rol == "Visualizador":
                visual_panel(df)
            else:
                st.error("Rol no reconocido")
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        st.warning("Por favor, sube un archivo CSV para comenzar.")
