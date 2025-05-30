import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Panel de Administración", layout="wide")

USUARIOS = {"admin": "admin123"}

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

def login():
    st.title("🔐 Login de Administrador")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.success(f"✅ Login exitoso. Bienvenido, {usuario}")
            st.experimental_rerun()
        else:
            st.error("❌ Credenciales incorrectas")

def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.experimental_rerun()

def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for i in range(len(df)):
        fila = ", ".join([str(x) for x in df.iloc[i]])
        pdf.cell(200, 10, txt=fila, ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    pdf_data = buffer.getvalue()
    return pdf_data

def generar_word(df):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

def admin_panel():
    st.title("🧰 Panel de Administración Avanzado")
    archivo = st.file_uploader("📂 Suba su archivo CSV", type=["csv"])
    if archivo:
        df = pd.read_csv(archivo)
        st.subheader("📈 Visualización de Datos")
        st.dataframe(df)

        st.markdown("### 📊 Gráficos de Series Temporales")
        columnas_numericas = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if columnas_numericas:
            opcion = st.selectbox("Seleccione columna para graficar", columnas_numericas)
            st.line_chart(df[opcion])
        else:
            st.warning("No hay columnas numéricas para graficar.")

        st.markdown("### 🔗 Matriz de Correlación")
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            fig = px.imshow(numeric_df.corr(), text_auto=True, title="Matriz de Correlación")
            st.plotly_chart(fig)
        else:
            st.warning("⚠️ No hay datos numéricos para mostrar una matriz de correlación.")

        st.markdown("### 📤 Exportar Reportes")
        col1, col2 = st.columns(2)
        with col1:
            pdf_data = generar_pdf(df)
            b64_pdf = base64.b64encode(pdf_data).decode()
            href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="reporte.pdf">📄 Descargar PDF</a>'
            st.markdown(href_pdf, unsafe_allow_html=True)
        with col2:
            word_data = generar_word(df)
            b64_word = base64.b64encode(word_data).decode()
            href_word = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="reporte.docx">📝 Descargar Word</a>'
            st.markdown(href_word, unsafe_allow_html=True)

        if st.button("🔓 Cerrar sesión"):
            logout()
    else:
        st.info("Por favor cargue un archivo para acceder a las herramientas.")

def main():
    if st.session_state.autenticado:
        admin_panel()
    else:
        login()

main()
