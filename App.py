import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document

# ----------------- Autenticación -----------------
USUARIOS = {
    "admin": {"password": "admin123", "rol": "admin"},
    "tecnico": {"password": "tecnico123", "rol": "tecnico"}
}

# ----------------- Login -----------------
def login():
    st.title("💧 Hydromet - Inicio de sesión")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario in USUARIOS and USUARIOS[usuario]["password"] == contraseña:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.rol = USUARIOS[usuario]["rol"]
            st.success(f"✅ Login exitoso. Bienvenido, {usuario}")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")

# ----------------- Logout -----------------
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.rol = ""
    st.rerun()

# ----------------- Generar PDF -----------------
def generar_pdf(df_to_export):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Datos", ln=True, align="C")
    pdf.ln()

    col_width = pdf.w / (len(df_to_export.columns) + 1)
    for col in df_to_export.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()

    for index, row in df_to_export.iterrows():
        if isinstance(index, pd.Timestamp):
            pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d')), border=1)
        else:
            pdf.cell(col_width, 10, str(index), border=1)
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output

# ----------------- Generar Word -----------------
def generar_word(df_to_export):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df_to_export.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df_to_export.columns):
        hdr_cells[i].text = col
    for index, row in df_to_export.iterrows():
        row_cells = table.add_row().cells
        for i, col_name in enumerate(df_to_export.columns):
            row_cells[i].text = str(row[col_name])
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ----------------- Panel de Administración -----------------
def admin_panel():
    st.title("🛠️ Hydromet - Panel de Administración")
    st.write(f"Bienvenido, {st.session_state.usuario}")

    if st.session_state.rol == "admin":
        st.subheader("📁 Cargar Datos (CSV)")
        uploaded_file = st.file_uploader("Sube tu archivo CSV para visualizar los datos", type=["csv"])
        if uploaded_file is None:
            st.session_state.df_cargado = None
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success("Archivo CSV cargado exitosamente.")
                if 'fecha' in df.columns:
                    try:
                        df['fecha'] = pd.to_datetime(df['fecha'])
                        df.set_index('fecha', inplace=True)
                        st.info("Columna 'fecha' detectada y establecida como índice de tiempo.")
                    except Exception as e:
                        st.warning(f"No se pudo convertir la columna 'fecha': {e}")
                elif st.checkbox("¿Tu archivo tiene una columna de fecha/hora para el índice?"):
                    date_column = st.selectbox("Selecciona la columna de fecha/hora:", df.columns)
                    if date_column:
                        try:
                            df[date_column] = pd.to_datetime(df[date_column])
                            df.set_index(date_column, inplace=True)
                            st.info(f"Columna '{date_column}' establecida como índice de tiempo.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                st.subheader("Vista Previa de los Datos")
                st.dataframe(df)
                st.session_state.df_cargado = df
            except Exception as e:
                st.error(f"Error al leer el archivo CSV: {e}")
                st.session_state.df_cargado = None

    df_actual = st.session_state.df_cargado

    if df_actual is not None and not df_actual.empty:
        numeric_df = df_actual.select_dtypes(include=['number'])

        if not numeric_df.empty:
            st.subheader("📈 Visualización de Datos")
            st.line_chart(df_actual)

            if st.session_state.rol == "admin":
                st.subheader("📊 Gráfico de Correlación")
                try:
                    fig = px.imshow(numeric_df.corr(), text_auto=True, title="Matriz de Correlación")
                    st.plotly_chart(fig)
                except Exception as e:
                    st.warning(f"Error en el gráfico de correlación: {e}")

            st.subheader("Exploración de Gráficos")
            columnas_numericas = numeric_df.columns.tolist()
            if len(columnas_numericas) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_axis = st.selectbox("Eje X:", options=columnas_numericas, key="scatter_x")
                with col2:
                    y_axis = st.selectbox("Eje Y:", options=columnas_numericas, key="scatter_y")
                if x_axis and y_axis:
                    try:
                        fig_scatter = px.scatter(df_actual, x=x_axis, y=y_axis, title=f"Dispersión {x_axis} vs {y_axis}")
                        st.plotly_chart(fig_scatter)
                    except Exception as e:
                        st.warning(f"Error al generar dispersión: {e}")
            else:
                st.info("Al menos dos columnas numéricas requeridas.")

            hist_column = st.selectbox("Columna para Histograma:", options=columnas_numericas, key="hist_col")
            if hist_column:
                try:
                    fig_hist = px.histogram(df_actual, x=hist_column, marginal="rug", title=f"Histograma de {hist_column}")
                    st.plotly_chart(fig_hist)
                except Exception as e:
                    st.warning(f"Error al generar histograma: {e}")

        else:
            st.warning("No hay columnas numéricas para graficar.")

        st.subheader("📤 Exportar Datos")
        pdf_data = generar_pdf(df_actual)
        word_data = generar_word(df_actual)

        st.download_button("📄 Descargar PDF", data=pdf_data, file_name="reporte.pdf", mime="application/pdf")
        st.download_button("📝 Descargar Word", data=word_data, file_name="reporte.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    else:
        if st.session_state.rol != "admin":
            st.info("Datos cargados previamente por el administrador.")

    if st.button("Cerrar sesión"):
        logout()

# ----------------- Inicialización -----------------
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.rol = ""
if 'df_cargado' not in st.session_state:
    st.session_state.df_cargado = None

# ----------------- Main -----------------
def main():
    if st.session_state.autenticado:
        admin_panel()
    else:
        login()

# Eliminar menú “Manage App” en despliegues externos
st.set_page_config(page_title="Hydromet", layout="wide", initial_sidebar_state="expanded")

main()
