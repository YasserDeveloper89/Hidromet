import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from fpdf import FPDF
from docx import Document
import base64

# ---------------------- CONFIGURACIÓN DE LA PÁGINA ----------------------
st.set_page_config(page_title="Hydromet", page_icon="💧", layout="wide")

# ---------------------- VARIABLES DE SESIÓN ----------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "df" not in st.session_state:
    st.session_state.df = None

# ---------------------- FUNCIONES DE USUARIO ----------------------
USUARIOS = {
    "admin": {"password": "admin123", "rol": "admin"},
    "tecnico": {"password": "tecnico123", "rol": "tecnico"},
}

def login():
    st.markdown("""
        <h2 style='text-align: center;'>💧 Hydromet</h2>
        <p style='text-align: center;'>Plataforma inteligente para el monitoreo, análisis y creación de reportes hidrometeorológicos</p>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario in USUARIOS and USUARIOS[usuario]["password"] == password:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.rol = USUARIOS[usuario]["rol"]
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

def logout():
    if st.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = ""
        st.session_state.rol = ""
        st.session_state.df = None
        st.rerun()

# ---------------------- FUNCIONES DE HERRAMIENTAS ----------------------
def cargar_datos():
    archivo = st.file_uploader("Sube tu archivo CSV para visualizar los datos", type=["csv"])
    if archivo is not None:
        try:
            st.session_state.df = pd.read_csv(archivo)
            st.success("Archivo cargado correctamente")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

def vista_previa():
    if st.session_state.df is not None:
        st.subheader("Vista previa de los datos")
        st.dataframe(st.session_state.df.head())

def matriz_correlacion():
    df = st.session_state.df
    try:
        df_num = df.select_dtypes(include=["float64", "int64"])
        st.subheader("Matriz de correlación")
        fig, ax = plt.subplots()
        sns.heatmap(df_num.corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"No se pudo generar la matriz de correlación: {e}")

def grafico_barras():
    df = st.session_state.df
    columnas = df.columns.tolist()
    columna = st.selectbox("Selecciona la columna para el gráfico de barras", columnas)
    fig = px.bar(df[columna].value_counts().reset_index(), x="index", y=columna, title=f"Distribución de {columna}")
    st.plotly_chart(fig)

def grafico_lineas():
    df = st.session_state.df
    columnas = df.columns.tolist()
    x = st.selectbox("Eje X", columnas, key="line_x")
    y = st.selectbox("Eje Y", columnas, key="line_y")
    fig = px.line(df, x=x, y=y, title=f"Gráfico de líneas: {x} vs {y}")
    st.plotly_chart(fig)

def grafico_dispersion():
    df = st.session_state.df
    columnas = df.columns.tolist()
    x = st.selectbox("Eje X", columnas, key="disp_x")
    y = st.selectbox("Eje Y", columnas, key="disp_y")
    fig = px.scatter(df, x=x, y=y, title=f"Gráfico de dispersión: {x} vs {y}")
    st.plotly_chart(fig)

def histograma():
    df = st.session_state.df
    columnas = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    columna = st.selectbox("Selecciona la columna numérica", columnas)
    fig = px.histogram(df, x=columna, title=f"Histograma de {columna}")
    st.plotly_chart(fig)

def analisis_estadistico():
    df = st.session_state.df
    st.subheader("Análisis estadístico")
    st.write(df.describe())

def exportar_pdf():
    df = st.session_state.df
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i, col in enumerate(df.columns):
        pdf.cell(40, 10, col, 1)
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(40, 10, str(item), 1)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    st.download_button("Descargar PDF", buffer, file_name="reporte.pdf")

def exportar_word():
    df = st.session_state.df
    doc = Document()
    doc.add_heading("Reporte de datos", 0)
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
    st.download_button("Descargar Word", buffer, file_name="reporte.docx")

# ---------------------- INTERFAZ PRINCIPAL ----------------------
def admin_panel():
    st.title("Panel de Administrador")
    logout()
    cargar_datos()
    if st.session_state.df is not None:
        vista_previa()
        matriz_correlacion()
        grafico_barras()
        grafico_lineas()
        grafico_dispersion()
        histograma()
        analisis_estadistico()
        exportar_pdf()
        exportar_word()

def tecnico_panel():
    st.title("Panel de Técnico")
    logout()
    cargar_datos()
    if st.session_state.df is not None:
        vista_previa()
        grafico_barras()
        grafico_lineas()
        exportar_pdf()
        exportar_word()

def main():
    if not st.session_state.autenticado:
        login()
    else:
        if st.session_state.rol == "admin":
            admin_panel()
        elif st.session_state.rol == "tecnico":
            tecnico_panel()

if __name__ == "__main__":
    main()
    
