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

st.set_page_config(page_title="Hidromet Admin Panel", layout="wide")

# ---- UTILIDADES ----
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.password = ""

def login():
    st.title("Inicio de sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Login exitoso. Bienvenido, {username}")
            st.experimental_rerun()
        else:
            st.error("❌ Credenciales inválidas")

# ---- FUNCIONES PARA EXPORTAR ----
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos", ln=1, align="C")
    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.multi_cell(0, 10, row)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

def export_word(df):
    doc = Document()
    doc.add_heading("Informe de Datos", level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, item in enumerate(row):
            row_cells[i].text = str(item)
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output

# ---- PÁGINA ADMIN ----
def admin_panel():
    st.sidebar.title("Panel de Administrador")
    st.sidebar.success(f"Sesión iniciada como {st.session_state.username}")

    if st.sidebar.button("Cerrar sesión"):
        logout()
        st.experimental_rerun()

    st.title("Panel de Control Avanzado")
    uploaded_file = st.file_uploader("📁 Subir archivo CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Datos cargados correctamente")

        tabs = st.tabs([
            "📊 Datos", "📈 Gráficos", "📉 Correlación", "📤 Exportar", 
            "📌 Estadísticas", "🧮 Matriz", "📦 Valores Nulos", "📐 Boxplots", 
            "📍 Mapa Geográfico", "🕒 Serie Temporal", "⚙️ Simulación", "🧠 IA básica"
        ])

        # TAB: Datos
        with tabs[0]:
            st.subheader("📋 Vista previa de los datos")
            st.dataframe(df, use_container_width=True)

        # TAB: Gráficos
        with tabs[1]:
            st.subheader("📈 Gráficos Interactivos")
            col = st.selectbox("Seleccionar columna para histograma", df.columns)
            fig = px.histogram(df, x=col)
            st.plotly_chart(fig, use_container_width=True)

        # TAB: Correlación
        with tabs[2]:
            st.subheader("🔗 Mapa de Correlación")
            numeric_df = df.select_dtypes(include='number')
            corr = numeric_df.corr()
            fig_corr = px.imshow(corr, text_auto=True, aspect="auto", title="Matriz de Correlación")
            st.plotly_chart(fig_corr, use_container_width=True)

        # TAB: Exportar
        with tabs[3]:
            st.subheader("📤 Exportar Informes")
            pdf = export_pdf(df)
            st.download_button("📄 Descargar PDF", pdf, file_name="informe.pdf")
            word = export_word(df)
            st.download_button("📝 Descargar Word", word, file_name="informe.docx")

        # TAB: Estadísticas
        with tabs[4]:
            st.subheader("📌 Estadísticas Descriptivas")
            st.dataframe(df.describe(), use_container_width=True)

        # TAB: Matriz
        with tabs[5]:
            st.subheader("📊 Matriz de Dispersión")
            fig = px.scatter_matrix(numeric_df)
            st.plotly_chart(fig, use_container_width=True)

        # TAB: Valores Nulos
        with tabs[6]:
            st.subheader("📦 Valores Nulos")
            st.write(df.isnull().sum())

        # TAB: Boxplots
        with tabs[7]:
            st.subheader("📐 Boxplots")
            col = st.selectbox("Seleccionar columna para Boxplot", numeric_df.columns)
            fig = px.box(df, y=col)
            st.plotly_chart(fig, use_container_width=True)

        # TAB: Mapa Geográfico
        with tabs[8]:
            st.subheader("🌍 Mapa Geográfico")
            if "lat" in df.columns and "lon" in df.columns:
                st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"}))
            else:
                st.warning("No se encontraron columnas 'lat' y 'lon'")

        # TAB: Serie Temporal
        with tabs[9]:
            st.subheader("🕒 Serie Temporal")
            if "fecha" in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])
                col = st.selectbox("Columna numérica para graficar", numeric_df.columns)
                fig = px.line(df, x='fecha', y=col)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se encontró una columna 'fecha'")

        # TAB: Simulación
        with tabs[10]:
            st.subheader("⚙️ Simulación de Datos")
            col = st.selectbox("Variable a simular", numeric_df.columns)
            ruido = st.slider("Nivel de ruido", 0.0, 1.0, 0.1)
            simulated = df[col] + np.random.normal(0, ruido, len(df))
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df[col], name="Original"))
            fig.add_trace(go.Scatter(y=simulated, name="Simulado"))
            st.plotly_chart(fig, use_container_width=True)

        # TAB: IA básica (placeholder)
        with tabs[11]:
            st.subheader("🤖 Predicción Básica (Placeholder)")
            st.info("Aquí podrías cargar un modelo de ML para análisis en tiempo real")

    else:
        st.warning("Por favor cargue un archivo para acceder a las herramientas")

# ---- CONTROL PRINCIPAL ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    admin_panel()
else:
    login()
    
