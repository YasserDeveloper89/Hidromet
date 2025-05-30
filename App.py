
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

st.set_page_config(page_title="Panel Hidromet", layout="wide")

# --- Gestión de sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Función para generar PDF ---
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
    pdf.ln(10)
    for i, row in df.iterrows():
        pdf.multi_cell(0, 10, txt=str(row.to_dict()))
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

# --- Función para generar DOCX ---
def generar_docx(df):
    doc = Document()
    doc.add_heading('Informe de Datos', 0)
    for i, row in df.iterrows():
        doc.add_paragraph(str(row.to_dict()))
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- Login ---
def login():
    with st.form("login_form"):
        st.subheader("Inicio de Sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar Sesión")
        if submit:
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.success("✅ Login exitoso. Bienvenido, admin")
                st.experimental_set_query_params(logged_in="true")
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")

# --- Logout ---
def logout():
    st.session_state.logged_in = False
    st.experimental_set_query_params()
    st.rerun()

# --- Panel de Administración ---
def admin_panel():
    st.sidebar.title("Menú de Administración")
    if st.sidebar.button("Cerrar Sesión"):
        logout()

    st.title("Panel de Administración Hidromet")
    st.markdown("### Carga y Visualización de Datos")

    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

        st.markdown("### Exportar Informes")
        col1, col2 = st.columns(2)
        with col1:
            pdf_data = generar_pdf(df)
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">📄 Descargar PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

        with col2:
            docx_data = generar_docx(df)
            b64 = base64.b64encode(docx_data).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">📝 Descargar Word</a>'
            st.markdown(href, unsafe_allow_html=True)

        st.markdown("### Herramientas de Análisis")
        st.subheader("1. Estadísticas Generales")
        st.write(df.describe())

        st.subheader("2. Valores Nulos")
        st.write(df.isnull().sum())

        st.subheader("3. Histograma de Columnas Numéricas")
        num_cols = df.select_dtypes(include=np.number).columns
        if len(num_cols) > 0:
            selected_col = st.selectbox("Selecciona columna", num_cols)
            fig = px.histogram(df, x=selected_col)
            st.plotly_chart(fig)
        
        st.subheader("4. Series Temporales")
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            df.set_index('fecha', inplace=True)
            for col in num_cols:
                st.line_chart(df[col])

        st.subheader("5. Matriz de Correlación")
        df_numeric = df.select_dtypes(include='number')
        if not df_numeric.empty:
            fig_corr = px.imshow(df_numeric.corr(), text_auto=True, color_continuous_scale='Viridis')
            st.plotly_chart(fig_corr)
        else:
            st.warning("No hay columnas numéricas suficientes.")

        st.subheader("6. Gráfico de Dispersión")
        if len(num_cols) >= 2:
            col_x = st.selectbox("Eje X", num_cols, key="disp_x")
            col_y = st.selectbox("Eje Y", num_cols, key="disp_y")
            st.plotly_chart(px.scatter(df, x=col_x, y=col_y))

        st.subheader("7. Boxplot de Variables")
        col_box = st.selectbox("Variable para Boxplot", num_cols, key="box")
        st.plotly_chart(px.box(df, y=col_box))

        st.subheader("8. Mapa de Calor (si hay lat/lon)")
        if 'lat' in df.columns and 'lon' in df.columns:
            st.map(df[['lat', 'lon']])

        st.subheader("9. Gráfico de Barras")
        col_bar = st.selectbox("Variable para gráfico de barras", df.columns, key="bar")
        st.plotly_chart(px.bar(df, x=col_bar))

        st.subheader("10. Exportar datos filtrados")
        filtro = st.text_input("Filtrar por valor exacto")
        if filtro:
            df_filtrado = df[df.astype(str).apply(lambda row: row.str.contains(filtro)).any(axis=1)]
            st.dataframe(df_filtrado)
            st.download_button("Descargar CSV filtrado", df_filtrado.to_csv(index=False), "filtro.csv", "text/csv")

    else:
        st.info("Por favor cargue un archivo CSV para comenzar.")

# --- Main ---
def main():
    if st.session_state.logged_in:
        admin_panel()
    else:
        login()

main()
