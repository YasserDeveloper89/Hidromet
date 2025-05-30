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

# Config
st.set_page_config(page_title="Panel de Hidrometeorología", layout="wide")

# Usuarios válidos
USUARIOS = {"admin": "admin123"}

# Sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# LOGIN
def login():
    with st.container():
        st.markdown("## Inicio de sesión")
        usuario = st.text_input("Usuario", key="usuario_input")
        clave = st.text_input("Contraseña", type="password", key="clave_input")
        login_btn = st.button("Iniciar sesión")

        if login_btn:
            if usuario in USUARIOS and USUARIOS[usuario] == clave:
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.success(f"✅ Login exitoso. Bienvenido, {usuario}")
            else:
                st.error("❌ Credenciales inválidas")

# LOGOUT
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.experimental_set_query_params()  # Limpia la URL
    st.success("✅ Sesión cerrada correctamente")

# EXPORTAR PDF
def exportar_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C")
        for i in range(len(df)):
            row = ', '.join([str(x) for x in df.iloc[i]])
            pdf.multi_cell(200, 10, txt=row)
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">📄 Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

# EXPORTAR WORD
def exportar_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe de Datos", 0)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = col
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">📝 Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar Word: {e}")

# HERRAMIENTAS ADMIN
def admin_panel(df):
    st.title("Panel de Administración Avanzado")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        exportar_pdf(df)
    with col2:
        exportar_word(df)

    st.subheader("1. Vista previa de datos")
    st.dataframe(df)

    st.subheader("2. Estadísticas descriptivas")
    st.write(df.describe())

    st.subheader("3. Histograma")
    col = st.selectbox("Selecciona una columna numérica", df.select_dtypes(include=np.number).columns)
    st.plotly_chart(px.histogram(df, x=col), use_container_width=True)

    st.subheader("4. Gráfico de líneas")
    st.plotly_chart(px.line(df), use_container_width=True)

    st.subheader("5. Mapa de calor (correlación)")
    corr_df = df.select_dtypes(include=np.number).corr()
    fig_corr = px.imshow(corr_df, text_auto=True, aspect="auto")
    st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("6. Dispersión entre variables")
    cols = df.select_dtypes(include=np.number).columns
    if len(cols) >= 2:
        x_col = st.selectbox("X", cols, key="scatter_x")
        y_col = st.selectbox("Y", cols, key="scatter_y")
        st.plotly_chart(px.scatter(df, x=x_col, y=y_col), use_container_width=True)

    st.subheader("7. Boxplot")
    col = st.selectbox("Columna", df.select_dtypes(include=np.number).columns, key="boxplot")
    st.plotly_chart(px.box(df, y=col), use_container_width=True)

    st.subheader("8. Gráfico de barras por categoría")
    cat_col = st.selectbox("Columna categórica", df.select_dtypes(exclude=np.number).columns, key="bar_cat")
    num_col = st.selectbox("Valor numérico", df.select_dtypes(include=np.number).columns, key="bar_num")
    st.plotly_chart(px.bar(df, x=cat_col, y=num_col), use_container_width=True)

    st.subheader("9. Tendencias con media móvil")
    trend_col = st.selectbox("Columna para tendencia", df.select_dtypes(include=np.number).columns, key="trend")
    df["media_movil"] = df[trend_col].rolling(window=3).mean()
    st.line_chart(df[[trend_col, "media_movil"]])

    st.subheader("10. Análisis de valores nulos")
    st.write(df.isnull().sum())

    st.subheader("11. Mapa (si hay lat/lon)")
    if "lat" in df.columns and "lon" in df.columns:
        st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"}))

    st.subheader("12. Filtro dinámico")
    filtro_col = st.selectbox("Columna para filtrar", df.columns)
    valores = df[filtro_col].unique()
    seleccion = st.multiselect("Selecciona valor(es)", valores)
    if seleccion:
        st.dataframe(df[df[filtro_col].isin(seleccion)])

    st.markdown("---")
    if st.button("🚪 Cerrar sesión"):
        logout()

# MAIN APP
def main():
    if not st.session_state.autenticado:
        login()
    else:
        st.sidebar.title("Panel de navegación")
        archivo = st.sidebar.file_uploader("📂 Cargar archivo CSV", type=["csv"])
        if archivo is not None:
            try:
                df = pd.read_csv(archivo)
                admin_panel(df)
            except Exception as e:
                st.error(f"Error al cargar archivo: {e}")
        else:
            st.warning("Por favor cargue un archivo para acceder a las herramientas.")

# RUN
if __name__ == "__main__":
    main()
