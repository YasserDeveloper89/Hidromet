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

# ------------------------- LOGIN & SESSION ----------------------------
def login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.title("🔐 Panel de Acceso Hidromet Premium")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login exitoso. Bienvenido, admin")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    return False

def logout():
    st.session_state.logged_in = False
    st.experimental_rerun()

# ------------------------- FUNCIONES PDF / WORD ------------------------
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Datos Hidromet", ln=True, align='C')
    pdf.ln(10)
    for index, row in df.iterrows():
        row_data = ' | '.join([str(elem) for elem in row])
        pdf.cell(200, 10, txt=row_data, ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.read()

def generar_word(df):
    doc = Document()
    doc.add_heading('Reporte de Datos Hidromet', 0)
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
    buffer.seek(0)
    return buffer.read()

# ------------------------- PANEL ADMINISTRADOR ------------------------
def admin_panel():
    st.title("🌐 Panel de Administración Hidromet Premium")
    st.sidebar.button("🔓 Cerrar sesión", on_click=logout)

    uploaded_file = st.sidebar.file_uploader("Subir archivo CSV", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df.set_index('fecha', inplace=True)

        st.dataframe(df.head())

        st.subheader("📈 Visualización de Datos")
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

        if numeric_cols:
            col_x = st.selectbox("Columna X", numeric_cols)
            col_y = st.selectbox("Columna Y", numeric_cols)
            fig = px.line(df, x=col_x, y=col_y, title="Gráfico de Líneas")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay columnas numéricas para graficar.")

        st.subheader("📊 Matriz de Correlación")
        numeric_df = df.select_dtypes(include='number')
        if not numeric_df.empty:
            fig_corr = px.imshow(numeric_df.corr(), text_auto=True, aspect="auto", title="Matriz de Correlación")
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.warning("No se encontraron datos numéricos para la correlación.")

        st.subheader("📤 Exportar Reportes")
        pdf_data = generar_pdf(df)
        word_data = generar_word(df)

        b64_pdf = base64.b64encode(pdf_data).decode()
        b64_word = base64.b64encode(word_data).decode()

        href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="reporte.pdf">📄 Descargar PDF</a>'
        href_word = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="reporte.docx">📝 Descargar Word</a>'

        st.markdown(href_pdf, unsafe_allow_html=True)
        st.markdown(href_word, unsafe_allow_html=True)

        st.subheader("🛠️ Herramientas Técnicas Adicionales")
        st.markdown("- Análisis estadístico básico")
        st.write(df.describe())

        st.markdown("- Valores nulos por columna")
        st.write(df.isnull().sum())

        st.markdown("- Histograma")
        selected_col = st.selectbox("Seleccionar columna para histograma", numeric_cols)
        st.plotly_chart(px.histogram(df, x=selected_col), use_container_width=True)

        st.markdown("- Boxplot")
        st.plotly_chart(px.box(df, y=selected_col), use_container_width=True)

        st.markdown("- Mapa de calor de valores nulos")
        st.plotly_chart(px.imshow(df.isnull(), color_continuous_scale='reds'), use_container_width=True)

    else:
        st.warning("Por favor cargue un archivo CSV para acceder a las herramientas.")

# ------------------------- MAIN ------------------------
def main():
    if login():
        admin_panel()

if __name__ == "__main__":
    main()
    
