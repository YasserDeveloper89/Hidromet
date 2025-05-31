import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document

st.set_page_config(page_title="Hydromet 💧", layout="wide")

# Autenticación simulada
USUARIOS = {
    "admin": {"password": "admin123", "rol": "administrador"},
    "tecnico": {"password": "tecnico123", "rol": "tecnico"}
}

def login():
    st.title("Hydromet 💧 - Inicio de sesión")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario in USUARIOS and USUARIOS[usuario]["password"] == password:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.rol = USUARIOS[usuario]["rol"]
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")

def logout():
    st.session_state.clear()
    st.stop()

def cargar_datos():
    archivo = st.file_uploader("Sube tu archivo CSV para visualizar los datos", type=["csv"])
    if archivo is not None:
        try:
            df = pd.read_csv(archivo)
            st.session_state["df_actual"] = df
            st.success("Archivo cargado correctamente.")
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

def visualizar_datos(df):
    st.subheader("Vista previa de los datos")
    st.dataframe(df)

def matriz_correlacion(df):
    st.subheader("Matriz de correlación")
    try:
        numeric_df = df.select_dtypes(include='number')
        if numeric_df.empty:
            st.warning("No hay columnas numéricas para correlación.")
        else:
            corr = numeric_df.corr()
            fig = px.imshow(corr, text_auto=True, aspect="auto", title="Matriz de Correlación")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la matriz de correlación: {e}")

def generar_pdf(df):
    st.subheader("Exportar datos a PDF")
    if st.button("Generar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        col_width = pdf.w / (len(df.columns) + 1)
        row_height = 6
        for col in df.columns:
            pdf.cell(col_width, row_height, str(col), border=1)
        pdf.ln(row_height)
        for index, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, row_height, str(item), border=1)
            pdf.ln(row_height)
        buffer = BytesIO()
        pdf.output(buffer)
        b64 = base64.b64encode(buffer.getvalue()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="datos.pdf">Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

def generar_word(df):
    st.subheader("Exportar datos a Word")
    if st.button("Generar Word"):
        doc = Document()
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
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="datos.docx">Descargar Word</a>'
        st.markdown(href, unsafe_allow_html=True)

def graficos_adicionales(df):
    st.subheader("Gráfico de barras")
    column_bar = st.selectbox("Selecciona una columna categórica", df.columns)
    if column_bar:
        try:
            data_bar = df[column_bar].value_counts().reset_index()
            data_bar.columns = [column_bar, "count"]
            fig_bar = px.bar(data_bar, x=column_bar, y="count", title=f"Distribución de {column_bar}")
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error en gráfico de barras: {e}")

    st.subheader("Gráfico de líneas")
    num_cols = df.select_dtypes(include='number').columns.tolist()
    if len(num_cols) >= 2:
        x_col = st.selectbox("Eje X", num_cols, index=0)
        y_col = st.selectbox("Eje Y", num_cols, index=1)
        fig_line = px.line(df, x=x_col, y=y_col, title=f"Gráfico de {y_col} vs {x_col}")
        st.plotly_chart(fig_line, use_container_width=True)

def admin_panel():
    st.title("Panel de Administración 💧")
    st.sidebar.success(f"Conectado como: {st.session_state.usuario}")
    if st.sidebar.button("💧 Cerrar sesión"):
        logout()

    cargar_datos()

    if "df_actual" in st.session_state:
        df = st.session_state["df_actual"]
        visualizar_datos(df)
        matriz_correlacion(df)
        graficos_adicionales(df)
        generar_pdf(df)
        generar_word(df)

def tecnico_panel():
    st.title("Panel Técnico 💧")
    st.sidebar.success(f"Conectado como: {st.session_state.usuario}")
    if st.sidebar.button("💧 Cerrar sesión"):
        logout()

    cargar_datos()

    if "df_actual" in st.session_state:
        df = st.session_state["df_actual"]
        visualizar_datos(df)
        generar_pdf(df)
        generar_word(df)

def main():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        login()
    else:
        rol = st.session_state.get("rol", "")
        if rol == "administrador":
            admin_panel()
        elif rol == "tecnico":
            tecnico_panel()
        else:
            st.error("Rol no reconocido.")

if __name__ == "__main__":
    main()
