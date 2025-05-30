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

st.set_page_config(page_title="Hidromet Panel Pro", layout="wide")

# Datos de acceso de ejemplo
USER_CREDENTIALS = {
    "admin": "admin123",
    "tecnico": "tecnico123"
}

def authenticate(username, password):
    return USER_CREDENTIALS.get(username) == password

def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""

    with st.form("login_form"):
        st.markdown("### Iniciar sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")

        if submit:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Login exitoso. Bienvenido, {username}")
            else:
                st.error("Credenciales inválidas")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.experimental_set_query_params()


def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=True, align="C")

    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.cell(200, 10, txt=row, ln=True, align="L")

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    b64 = base64.b64encode(pdf_output.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">Descargar PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

def export_word(df):
    doc = Document()
    doc.add_heading('Informe de Datos Hidrometeorológicos', 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for index, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, item in enumerate(row):
            row_cells[i].text = str(item)
    word_output = BytesIO()
    doc.save(word_output)
    word_output.seek(0)
    b64 = base64.b64encode(word_output.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">Descargar Word</a>'
    st.markdown(href, unsafe_allow_html=True)

def admin_tools(df):
    st.title("Panel de Administración")
    st.button("Cerrar sesión", on_click=logout)
    st.markdown("---")

    st.subheader("1. Vista General de Datos")
    st.dataframe(df)

    st.subheader("2. Estadísticas Básicas")
    st.write(df.describe())

    st.subheader("3. Gráfico de Líneas")
    st.line_chart(df.select_dtypes(include=np.number))

    st.subheader("4. Gráfico de Barras")
    for column in df.select_dtypes(include=np.number).columns:
        st.bar_chart(df[column])

    st.subheader("5. Histograma")
    for column in df.select_dtypes(include=np.number).columns:
        fig = px.histogram(df, x=column, nbins=20)
        st.plotly_chart(fig)

    st.subheader("6. Matriz de Correlación")
    corr = df.select_dtypes(include=np.number).corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto")
    st.plotly_chart(fig_corr)

    st.subheader("7. Exportar Datos")
    export_pdf(df)
    export_word(df)

    st.subheader("8. Filtrado de Datos Avanzado")
    column = st.selectbox("Columna para filtrar", df.columns)
    value = st.text_input("Valor a filtrar")
    if value:
        st.write(df[df[column].astype(str).str.contains(value)])

    st.subheader("9. Gráfico Personalizado")
    x = st.selectbox("Eje X", df.select_dtypes(include=np.number).columns)
    y = st.selectbox("Eje Y", df.select_dtypes(include=np.number).columns)
    fig_custom = px.scatter(df, x=x, y=y)
    st.plotly_chart(fig_custom)

    st.subheader("10. Datos en Tiempo Real (Simulado)")
    realtime_data = df.sample(5)
    st.write(realtime_data)

    st.subheader("11. Gráficos Avanzados")
    for col in df.select_dtypes(include=np.number).columns[:2]:
        fig = go.Figure()
        fig.add_trace(go.Box(y=df[col], name=col))
        st.plotly_chart(fig)

    st.subheader("12. Información de la Fecha")
    df['Fecha'] = pd.to_datetime(df.iloc[:,0], errors='coerce')
    st.line_chart(df.set_index('Fecha').select_dtypes(include=np.number))

    st.subheader("13. Mapa (si hay datos de ubicación)")
    if 'lat' in df.columns and 'lon' in df.columns:
        st.map(df[['lat', 'lon']])

    st.subheader("14. Exportar a CSV")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar CSV", csv, "informe.csv", "text/csv")

    st.subheader("15. Información Técnica del Sistema")
    st.code(str(df.info()))

def main():
    login()
    if st.session_state.get("authenticated"):
        uploaded_file = st.file_uploader("Sube tu archivo de datos (.csv)", type=["csv"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                admin_tools(df)
            except Exception as e:
                st.error(f"Ocurrió un error al cargar el archivo: {e}")
        else:
            st.warning("Por favor cargue un archivo para acceder a las herramientas")

main()
    
