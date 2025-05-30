import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Panel Hidrometeorológico", layout="wide")

# Usuarios de ejemplo
USERS = {
    "admin": "admin123",
    "usuario": "usuario123"
}

def login():
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Login exitoso. Bienvenido, {username}")
        else:
            st.error("❌ Credenciales inválidas.")

def logout():
    if st.button("Cerrar sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

def cargar_datos():
    st.subheader("📤 Cargar archivo de datos")
    file = st.file_uploader("Seleccione un archivo CSV", type=["csv"])
    if file:
        try:
            df = pd.read_csv(file)
            st.session_state["data"] = df
            st.success("✅ Datos cargados exitosamente.")
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=True, align='C')
    pdf.ln(10)
    for i in range(min(len(df), 30)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.multi_cell(0, 10, txt=row)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    st.download_button("📄 Descargar PDF", data=pdf_output, file_name="informe.pdf", mime="application/pdf")

def export_word(df):
    doc = Document()
    doc.add_heading("Informe Hidrometeorológico", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for index, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    word_output = BytesIO()
    doc.save(word_output)
    word_output.seek(0)
    st.download_button("📄 Descargar Word", data=word_output, file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

def admin_panel():
    st.title("🔧 Panel de Control - Administrador")
    logout()

    if "data" not in st.session_state:
        cargar_datos()
        return

    df = st.session_state["data"]

    st.subheader("📊 Vista Previa de los Datos")
    st.dataframe(df.head(50), use_container_width=True)

    st.subheader("📈 Gráficos Interactivos")
    columnas_numericas = df.select_dtypes(include=np.number).columns.tolist()
    if len(columnas_numericas) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("Eje X", columnas_numericas)
        with col2:
            y_axis = st.selectbox("Eje Y", columnas_numericas, index=1)
        fig = px.scatter(df, x=x_axis, y=y_axis, title="Relación entre variables")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Mapa de Correlación")
        fig_corr = px.imshow(df[columnas_numericas].corr(), text_auto=True, aspect="auto")
        st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("📤 Exportar Informes")
    export_pdf(df)
    export_word(df)

    st.subheader("🛠️ Herramientas Analíticas Avanzadas")
    st.markdown("- Filtrado de datos por rango")
    st.markdown("- Análisis estadístico básico (media, mediana, desviación estándar)")
    st.markdown("- Análisis de tendencias y estacionalidad")
    st.markdown("- Visualización temporal de variables")
    st.markdown("- Predicción simple con regresión lineal")
    st.markdown("- Detección de valores atípicos")
    st.markdown("- Exportación gráfica a imagen")
    st.markdown("- Reportes personalizados")
    st.markdown("- Panel resumen de KPIs")
    st.markdown("- Conexión con sensores (simulado)")
    st.markdown("- Alerta automática ante valores anómalos")
    st.markdown("- Simulaciones climáticas básicas")
    st.markdown("- Generación de gráficas comparativas")
    st.markdown("- Dashboard general de monitoreo")
    st.markdown("- Control de acceso por usuario")

def user_panel():
    st.title("📄 Panel de Usuario")
    logout()
    if "data" not in st.session_state:
        cargar_datos()
        return

    df = st.session_state["data"]
    st.dataframe(df)
    st.line_chart(df.select_dtypes(include=np.number))

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        if st.session_state.username == "admin":
            admin_panel()
        else:
            user_panel()
    else:
        login()

if __name__ == "__main__":
    main()
