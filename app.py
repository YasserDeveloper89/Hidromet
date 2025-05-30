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

# ---------------------- SESSION HANDLING ----------------------
def initialize_session():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ''

# ---------------------- LOGIN ----------------------
def login():
    st.title("Inicio de sesión - HidroMet Premium Pro")
    username = st.text_input("Usuario", key="username_input")
    password = st.text_input("Contraseña", type="password", key="password_input")
    if st.button("Iniciar sesión"):
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Credenciales inválidas")

# ---------------------- LOGOUT ----------------------
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ''
    st.rerun()

# ---------------------- PDF EXPORT ----------------------
def export_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=True, align='C')
        for i in range(len(df)):
            row = ', '.join([str(x) for x in df.iloc[i]])
            pdf.cell(200, 10, txt=row, ln=True)
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        b64 = base64.b64encode(pdf_output.getvalue()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

# ---------------------- WORD EXPORT ----------------------
def export_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe de Datos Hidrometeorológicos", 0)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)
        for index, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)
        buffer = BytesIO()
        doc.save(buffer)
        b64 = base64.b64encode(buffer.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

# ---------------------- DASHBOARD ----------------------
def admin_panel():
    st.title("Panel de Administración - HidroMet Premium Pro")
    st.sidebar.button("Cerrar sesión", on_click=logout)

    uploaded_file = st.file_uploader("Cargar archivo CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("Archivo cargado exitosamente.")

        tabs = st.tabs([
            "📊 Vista General", "📈 Gráficos", "📌 Correlación", "🧮 Estadísticas",
            "🔍 Búsqueda", "📥 Exportar", "🔝 Top Valores", "📅 Fechas",
            "🧾 Resumen", "📡 Conexión Real"
        ])

        with tabs[0]:
            st.dataframe(df)

        with tabs[1]:
            for col in df.select_dtypes(include=np.number).columns:
                st.plotly_chart(px.line(df, y=col, title=f"Serie temporal: {col}"))

        with tabs[2]:
            numeric_df = df.select_dtypes(include=np.number)
            fig = px.imshow(numeric_df.corr(), text_auto=True, aspect="auto")
            st.plotly_chart(fig)

        with tabs[3]:
            st.write("Estadísticas descriptivas")
            st.write(df.describe())

        with tabs[4]:
            search = st.text_input("Buscar por palabra clave")
            if search:
                st.dataframe(df[df.apply(lambda row: row.astype(str).str.contains(search).any(), axis=1)])

        with tabs[5]:
            st.write("Exportar informe")
            export_pdf(df)
            export_word(df)

        with tabs[6]:
            for col in df.select_dtypes(include=np.number).columns:
                st.bar_chart(df[col].nlargest(10))

        with tabs[7]:
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])
                st.line_chart(df.set_index('fecha'))

        with tabs[8]:
            st.write("Resumen de columnas")
            st.write(df.dtypes)
            st.write(df.memory_usage())

        with tabs[9]:
            st.info("Simulación de conexión a sensores...")
            st.metric(label="Temperatura actual", value="23.5 ºC")
            st.metric(label="Humedad", value="75%")
            st.metric(label="Presión", value="1013 hPa")

    else:
        st.warning("Por favor cargue un archivo para acceder a las herramientas.")

# ---------------------- MAIN ----------------------
def main():
    initialize_session()
    if not st.session_state.authenticated:
        login()
    else:
        admin_panel()

if __name__ == '__main__':
    main()
    
