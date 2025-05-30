import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from docx import Document
import base64

# ---------------------- CONFIGURAR LA PÁGINA ----------------------
st.set_page_config(page_title="Panel Hidromet Pro", layout="wide")

# ---------------------- USUARIOS ----------------------
USUARIOS = {
    "admin": {"password": "admin123", "rol": "administrador"},
    "tecnico": {"password": "tec456", "rol": "tecnico"},
    "analista": {"password": "ana789", "rol": "analista"},
}

# ---------------------- SESSION STATE INIT ----------------------
if "login_state" not in st.session_state:
    st.session_state.login_state = False
    st.session_state.username = ""
    st.session_state.rol = ""

# ---------------------- FUNCIONES ----------------------
def login():
    with st.form("login_form"):
        st.subheader("Acceso a Hidromet PRO")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión")

        if submitted:
            if username in USUARIOS and USUARIOS[username]["password"] == password:
                st.session_state.login_state = True
                st.session_state.username = username
                st.session_state.rol = USUARIOS[username]["rol"]
                st.success(f"Bienvenido, {username}")
            else:
                st.error("Credenciales inválidas")

def logout():
    st.session_state.login_state = False
    st.session_state.username = ""
    st.session_state.rol = ""

# ---------------------- EXPORTAR PDF ----------------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
    pdf.ln()
    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.multi_cell(0, 10, row)
    temp_pdf = BytesIO()
    pdf.output(temp_pdf, dest='F')
    temp_pdf.seek(0)
    return temp_pdf

# ---------------------- EXPORTAR WORD ----------------------
def export_word(df):
    doc = Document()
    doc.add_heading("Informe de Datos Hidromet", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col_name in enumerate(df.columns):
        hdr_cells[i].text = str(col_name)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, cell in enumerate(row):
            row_cells[i].text = str(cell)
    temp_docx = BytesIO()
    doc.save(temp_docx)
    temp_docx.seek(0)
    return temp_docx

# ---------------------- PANEL ADMINISTRADOR ----------------------
def panel_admin(df):
    st.title("Panel Administrador 🔒")
    st.write("Control total del sistema. Accede a herramientas avanzadas:")

    st.subheader("1. Vista general del dataset")
    st.dataframe(df)

    st.subheader("2. Estadísticas descriptivas")
    st.write(df.describe())

    st.subheader("3. Histograma")
    col = st.selectbox("Seleccionar columna para histograma", df.columns)
    st.plotly_chart(px.histogram(df, x=col))

    st.subheader("4. Mapa de correlación")
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        st.plotly_chart(px.imshow(numeric_df.corr(), text_auto=True))
    else:
        st.warning("No hay columnas numéricas para generar mapa de correlación")

    st.subheader("5. Exportar Informes")
    col1, col2 = st.columns(2)
    with col1:
        pdf_bytes = export_pdf(df)
        st.download_button("Descargar PDF", pdf_bytes, file_name="informe.pdf")
    with col2:
        word_bytes = export_word(df)
        st.download_button("Descargar Word", word_bytes, file_name="informe.docx")

    st.subheader("6. Medición en Tiempo Real (Simulada)")
    if st.button("Obtener datos en tiempo real"):
        simulated = pd.DataFrame({
            "Sensor": ["S1", "S2", "S3"],
            "Valor": np.random.uniform(10, 50, 3),
            "Unidad": ["m/s", "L/s", "°C"]
        })
        st.table(simulated)

    st.subheader("7. Análisis por Rango de Fechas")
    start_date = st.date_input("Fecha inicio")
    end_date = st.date_input("Fecha fin")
    st.write("(Simulado) Datos entre fechas seleccionadas")

    st.subheader("8. Control de usuarios")
    st.write("(Simulado) Lista de usuarios, permisos y logs")

    st.subheader("9. Dashboard comparativo")
    st.write("(Simulado) Gráficos comparativos entre sensores")

    st.subheader("10. Alertas y Umbrales")
    st.write("(Simulado) Definición de umbrales y notificaciones")

    st.subheader("11. Integración con Equipos")
    st.write("(Simulado) Conexion a estaciones y sensores")

    st.subheader("12. Configuración avanzada")
    st.write("(Simulado) Opciones de backup, restauración, API, etc.")

    st.subheader("13. Reportes mensuales")
    st.write("(Simulado) Generación y descarga de reportes por mes")

    st.subheader("14. Estadísticas de rendimiento")
    st.write("(Simulado) Estadísticas del sistema, latencia, uptime")

    st.subheader("15. Logout")
    if st.button("Cerrar sesión"):
        logout()

# ---------------------- MAIN APP ----------------------
if not st.session_state.login_state:
    login()
else:
    uploaded_file = st.file_uploader("Sube archivo de datos (CSV)", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if st.session_state.rol == "administrador":
                panel_admin(df)
            else:
                st.write("Panel para otros roles en desarrollo...")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    
