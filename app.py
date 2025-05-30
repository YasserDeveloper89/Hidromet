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

st.set_page_config(page_title="Hidromet Pro Panel", layout="wide")

USUARIOS = {"admin": "admin123"}

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None

# Login
if not st.session_state.autenticado:
    st.title("Acceso al Panel Hidromet Pro")
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión")
        if submitted:
            if usuario in USUARIOS and USUARIOS[usuario] == password:
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.success(f"Bienvenido, {usuario}")
            else:
                st.error("Credenciales incorrectas")
else:
    st.sidebar.title(f"Usuario: {st.session_state.usuario}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.experimental_rerun()

    st.title("Panel de Administración Hidromet Premium")

    archivo = st.sidebar.file_uploader("Sube archivo CSV", type=["csv"])

    if archivo:
        try:
            df = pd.read_csv(archivo)

            st.subheader("1. Vista previa de datos")
            st.dataframe(df)

            st.subheader("2. Estadísticas descriptivas")
            st.write(df.describe())

            st.subheader("3. Histograma")
            num_cols = df.select_dtypes(include=np.number).columns.tolist()
            if num_cols:
                col_hist = st.selectbox("Selecciona columna", num_cols, key="hist")
                st.plotly_chart(px.histogram(df, x=col_hist), use_container_width=True)

            st.subheader("4. Gráfico de línea")
            st.plotly_chart(px.line(df[num_cols]), use_container_width=True)

            st.subheader("5. Mapa de calor de correlación")
            corr = df[num_cols].corr()
            fig = px.imshow(corr, text_auto=True, aspect="auto")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("6. Diagrama de dispersión")
            if len(num_cols) >= 2:
                x = st.selectbox("Eje X", num_cols, key="x")
                y = st.selectbox("Eje Y", num_cols, key="y")
                st.plotly_chart(px.scatter(df, x=x, y=y), use_container_width=True)

            st.subheader("7. Boxplot")
            box_col = st.selectbox("Columna para boxplot", num_cols, key="box")
            st.plotly_chart(px.box(df, y=box_col), use_container_width=True)

            st.subheader("8. Gráfico de barras por categoría")
            cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
            if cat_cols:
                cat = st.selectbox("Categoría", cat_cols)
                val = st.selectbox("Valor", num_cols, key="bar")
                st.plotly_chart(px.bar(df, x=cat, y=val), use_container_width=True)

            st.subheader("9. Tendencias con media móvil")
            trend = st.selectbox("Serie temporal", num_cols, key="trend")
            df['media_movil'] = df[trend].rolling(window=3).mean()
            st.line_chart(df[[trend, 'media_movil']])

            st.subheader("10. Valores nulos")
            st.write(df.isnull().sum())

            st.subheader("11. Mapa si hay coordenadas")
            if 'lat' in df.columns and 'lon' in df.columns:
                st.map(df.rename(columns={'lat': 'latitude', 'lon': 'longitude'}))

            st.subheader("12. Exportar PDF y Word")

            def export_pdf():
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                for i in range(len(df)):
                    row = ', '.join([str(x) for x in df.iloc[i]])
                    pdf.multi_cell(0, 10, row)
                buffer = BytesIO()
                pdf.output(buffer)
                b64 = base64.b64encode(buffer.getvalue()).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

            def export_word():
                doc = Document()
                doc.add_heading("Informe", 0)
                table = doc.add_table(rows=1, cols=len(df.columns))
                for i, col in enumerate(df.columns):
                    table.rows[0].cells[i].text = col
                for _, row in df.iterrows():
                    cells = table.add_row().cells
                    for i, val in enumerate(row):
                        cells[i].text = str(val)
                buffer = BytesIO()
                doc.save(buffer)
                b64 = base64.b64encode(buffer.getvalue()).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">Descargar Word</a>'
                st.markdown(href, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                export_pdf()
            with col2:
                export_word()

        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
    else:
        st.warning("Sube un archivo para acceder a las herramientas.")
                
