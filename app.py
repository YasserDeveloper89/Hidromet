import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
import base64
from datetime import datetime

# Seguridad de login
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Funciones de sesión

def login():
    st.title("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.username = username
        else:
            st.error("Credenciales inválidas")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.experimental_rerun()

# Exportación a PDF y Word

def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Datos Hidromet", ln=True, align='C')
    for i, row in df.iterrows():
        linea = ' | '.join(str(x) for x in row)
        pdf.multi_cell(0, 10, linea)
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

def generar_word(df):
    doc = Document()
    doc.add_heading('Informe de Datos Hidromet', 0)
    t = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = t.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for i, row in df.iterrows():
        row_cells = t.add_row().cells
        for j, value in enumerate(row):
            row_cells[j].text = str(value)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# Panel de herramientas

def admin_panel():
    st.title("Panel de Administración")
    st.sidebar.button("Cerrar sesión", on_click=logout)
    
    uploaded_file = st.file_uploader("Sube tu archivo de datos (.csv)", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("Datos cargados correctamente")

        st.subheader("Vista previa de datos")
        st.dataframe(df.head())

        st.subheader("Herramientas disponibles")
        herramientas = [
            "Estadísticas generales", "Histograma", "Boxplot", "Tendencia temporal",
            "Mapa de calor de correlaciones", "Gráficos de dispersión",
            "Gráficos de línea interactivos", "Agrupación por categorías",
            "Resumen por día/mes/año", "Filtrado avanzado de datos",
            "Exportar a PDF", "Exportar a Word"
        ]

        for tool in herramientas:
            st.markdown(f"### {tool}")
            if tool == "Estadísticas generales":
                st.write(df.describe())
            elif tool == "Histograma":
                col = st.selectbox("Selecciona una columna numérica", df.select_dtypes('number').columns, key="hist")
                st.plotly_chart(px.histogram(df, x=col))
            elif tool == "Boxplot":
                col = st.selectbox("Columna para boxplot", df.select_dtypes('number').columns, key="box")
                st.plotly_chart(px.box(df, y=col))
            elif tool == "Tendencia temporal":
                time_col = st.selectbox("Columna de fecha", df.columns, key="time")
                value_col = st.selectbox("Valor a analizar", df.select_dtypes('number').columns, key="trend")
                df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
                df = df.dropna(subset=[time_col])
                st.plotly_chart(px.line(df, x=time_col, y=value_col))
            elif tool == "Mapa de calor de correlaciones":
                corr = df.select_dtypes('number').corr()
                st.plotly_chart(px.imshow(corr, text_auto=True))
            elif tool == "Gráficos de dispersión":
                x = st.selectbox("X", df.select_dtypes('number').columns, key="scatter_x")
                y = st.selectbox("Y", df.select_dtypes('number').columns, key="scatter_y")
                st.plotly_chart(px.scatter(df, x=x, y=y))
            elif tool == "Gráficos de línea interactivos":
                col = st.selectbox("Columna numérica", df.select_dtypes('number').columns, key="line")
                st.plotly_chart(px.line(df[col]))
            elif tool == "Agrupación por categorías":
                group_col = st.selectbox("Columna de agrupación", df.columns, key="group")
                agg_col = st.selectbox("Columna para agregar", df.select_dtypes('number').columns, key="agg")
                st.bar_chart(df.groupby(group_col)[agg_col].mean())
            elif tool == "Resumen por día/mes/año":
                date_col = st.selectbox("Columna de fecha", df.columns, key="resumen")
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df['Año'] = df[date_col].dt.year
                st.write(df.groupby('Año').mean(numeric_only=True))
            elif tool == "Filtrado avanzado de datos":
                filtro = st.text_input("Expresión de filtro (ej. df['col'] > 50)")
                try:
                    filtered_df = df.query(filtro)
                    st.dataframe(filtered_df)
                except:
                    st.warning("Expresión no válida")
            elif tool == "Exportar a PDF":
                pdf_data = generar_pdf(df)
                b64 = base64.b64encode(pdf_data).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="informe.pdf">Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
            elif tool == "Exportar a Word":
                word_data = generar_word(df)
                b64 = base64.b64encode(word_data).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="informe.docx">Descargar Word</a>'
                st.markdown(href, unsafe_allow_html=True)

    else:
        st.warning("Por favor cargue un archivo para acceder a las herramientas")

# Main
if __name__ == '__main__':
    if not st.session_state.authenticated:
        login()
    else:
        admin_panel()
    
