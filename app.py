
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from io import BytesIO
from docx import Document
from fpdf import FPDF

st.set_page_config(page_title="HydroClima Pro", layout="wide")

# --- Sidebar ---
st.sidebar.image("assets/logo.png", width=150)
st.sidebar.title("HydroClima Pro")
st.sidebar.markdown("Gestión meteorológica e hidrológica")

menu = st.sidebar.radio("Navegación", ["Carga de Datos", "Visualización", "Mapa", "Campañas", "Generar Informe"])

# --- Funciones auxiliares ---
def guardar_pdf(dataframe, filename="informe.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Informe de Datos Hidrometeorológicos", ln=True, align='C')
    pdf.ln(10)
    for col in dataframe.columns:
        pdf.cell(40, 8, col, 1)
    pdf.ln()
    for i, row in dataframe.iterrows():
        for val in row:
            pdf.cell(40, 8, str(val)[:15], 1)
        pdf.ln()
    pdf.output(filename)

def guardar_word(dataframe, filename="informe.docx"):
    doc = Document()
    doc.add_heading('Informe de Datos Hidrometeorológicos', 0)
    table = doc.add_table(rows=1, cols=len(dataframe.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(dataframe.columns):
        hdr_cells[i].text = col
    for index, row in dataframe.iterrows():
        row_cells = table.add_row().cells
        for i, value in enumerate(row):
            row_cells[i].text = str(value)
    doc.save(filename)

# --- Módulo: Carga de Datos ---
if menu == "Carga de Datos":
    st.title("📥 Carga de Datos")
    archivo = st.file_uploader("Sube tu archivo de datos (CSV, Excel, JSON)", type=["csv", "xlsx", "json"])
    if archivo:
        try:
            if archivo.name.endswith(".csv"):
                df = pd.read_csv(archivo)
            elif archivo.name.endswith(".xlsx"):
                df = pd.read_excel(archivo)
            elif archivo.name.endswith(".json"):
                df = pd.read_json(archivo)
            st.session_state["datos"] = df
            st.success("Datos cargados correctamente")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error al cargar los datos: {e}")

# --- Módulo: Visualización ---
elif menu == "Visualización":
    st.title("📊 Visualización Interactiva")
    if "datos" in st.session_state:
        df = st.session_state["datos"]
        col_x = st.selectbox("Selecciona variable X:", df.columns)
        col_y = st.selectbox("Selecciona variable Y:", df.columns)
        fig = px.scatter(df, x=col_x, y=col_y, title="Gráfico de Dispersión")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Primero debes cargar un archivo en la sección anterior.")

# --- Módulo: Mapa ---
elif menu == "Mapa":
    st.title("🗺️ Mapa de Estaciones")
    if "datos" in st.session_state:
        df = st.session_state["datos"]
        if "lat" in df.columns and "lon" in df.columns:
            m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=6)
            for _, row in df.iterrows():
                folium.Marker(location=[row["lat"], row["lon"]], popup=str(row)).add_to(m)
            st_folium(m, use_container_width=True, height=500)
        else:
            st.error("Los datos deben tener columnas 'lat' y 'lon' para mostrar el mapa.")
    else:
        st.warning("Primero debes cargar un archivo en la sección anterior.")

# --- Módulo: Campañas ---
elif menu == "Campañas":
    st.title("📁 Gestión de Campañas de Medición")
    nombre = st.text_input("Nombre de campaña")
    fecha = st.date_input("Fecha de inicio")
    equipo = st.text_area("Equipo de trabajo")
    st.write("Añade observaciones adicionales:")
    obs = st.text_area("Observaciones")
    if st.button("Guardar campaña"):
        st.success(f"Campaña '{nombre}' guardada correctamente.")

# --- Módulo: Informe ---
elif menu == "Generar Informe":
    st.title("📄 Generar Informe")
    if "datos" in st.session_state:
        df = st.session_state["datos"]
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Exportar PDF"):
                guardar_pdf(df)
                with open("informe.pdf", "rb") as f:
                    st.download_button("Descargar PDF", data=f, file_name="informe.pdf")
        with col2:
            if st.button("📝 Exportar Word"):
                guardar_word(df)
                with open("informe.docx", "rb") as f:
                    st.download_button("Descargar Word", data=f, file_name="informe.docx")
    else:
        st.warning("Primero debes cargar un archivo en la sección de carga de datos.")
