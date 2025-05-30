import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import base64

# ----------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ----------------------------------------
st.set_page_config(page_title="HydroClimaPRO Admin", layout="wide")

# ----------------------------------------
# SIMULACIÓN DE USUARIOS
# ----------------------------------------
usuarios = {
    "admin": "admin123",
    "supervisor": "super456",
    "tecnico": "tec789"
}

st.sidebar.title("Inicio de sesión")
nombre_usuario = st.sidebar.text_input("Usuario")
password = st.sidebar.text_input("Contraseña", type="password")
login = st.sidebar.button("Ingresar")

# ----------------------------------------
# FUNCIONES AUXILIARES
# ----------------------------------------
def generar_pdf(df, resumen):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=1, align="C")
    pdf.ln(10)
    pdf.multi_cell(0, 10, resumen)
    pdf.ln(10)
    for col in df.columns:
        pdf.cell(40, 10, col, 1)
    pdf.ln()
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(40, 10, str(val), 1)
        pdf.ln()
    output = BytesIO()
    pdf.output(output)
    return output.getvalue()

def generar_word(df, resumen):
    doc = Document()
    doc.add_heading("Informe de Datos Hidrometeorológicos", 0)
    doc.add_paragraph(resumen)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    output = BytesIO()
    doc.save(output)
    return output.getvalue()

def mostrar_grafico(df):
    st.subheader("Visualización Interactiva")
    columna = st.selectbox("Selecciona columna numérica:", df.select_dtypes(include=np.number).columns)
    if columna:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[columna], mode='lines+markers', name=columna))
        fig.update_layout(template="plotly_dark", title=f"Tendencia de {columna}")
        st.plotly_chart(fig, use_container_width=True)

def mostrar_estadisticas(df):
    st.subheader("Estadísticas Detalladas")
    st.write(df.describe())
    st.subheader("Matriz de Correlación")
    corr = df.select_dtypes(include=np.number).corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, ax=ax, cmap="coolwarm")
    st.pyplot(fig)

# ----------------------------------------
# LÓGICA PRINCIPAL
# ----------------------------------------
if login and nombre_usuario in usuarios and usuarios[nombre_usuario] == password:
    st.success(f"Bienvenido, {nombre_usuario.upper()} 👋")
    st.title("HydroClimaPRO - Panel Principal")

    uploaded_file = st.file_uploader("Carga un archivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())

        tab1, tab2, tab3 = st.tabs(["Visualización", "Estadísticas", "Informe"])

        with tab1:
            mostrar_grafico(df)

        with tab2:
            mostrar_estadisticas(df)

        with tab3:
            st.subheader("Generar Informe")
            resumen = st.text_area("Resumen del informe")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Descargar PDF"):
                    try:
                        pdf_bytes = generar_pdf(df, resumen)
                        st.download_button(label="Descargar PDF", data=pdf_bytes, file_name="informe.pdf", mime="application/pdf")
                    except Exception as e:
                        st.error(f"Error al generar PDF: {e}")
            with col2:
                if st.button("Descargar Word"):
                    try:
                        word_bytes = generar_word(df, resumen)
                        st.download_button(label="Descargar Word", data=word_bytes, file_name="informe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    except Exception as e:
                        st.error(f"Error al generar Word: {e}")

        if nombre_usuario == "admin":
            st.markdown("---")
            st.header("Panel Administrativo")
            st.write("Gestión de sensores, usuarios y módulos avanzados")
            st.button("Simular conexión a sensor")
            st.write("(Conexión real requiere puerto y hardware específico)")

            if st.button("Generar datos simulados"):
                sim = pd.DataFrame({
                    "Fecha": pd.date_range(start='2024-01-01', periods=100),
                    "Temp": np.random.normal(20, 5, 100),
                    "Humedad": np.random.uniform(40, 90, 100),
                    "Presión": np.random.normal(1010, 10, 100)
                })
                st.dataframe(sim)
                st.line_chart(sim.set_index("Fecha"))

else:
    st.warning("Por favor, ingresa credenciales válidas para acceder.")
    
