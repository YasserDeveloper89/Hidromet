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
    "admin": "admin123",
    "tecnico": "tecnico123"
}

# ----------------- Login -----------------
def login():
    st.title("💧 Hydromet - Inicio de sesion")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario in USUARIOS and USUARIOS[usuario] == contrasena:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.success(f"✅ Login exitoso. Bienvenido, {usuario}")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")

# ----------------- Logout -----------------
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
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

    st.subheader("📁 Cargar Datos (CSV)")
    uploaded_file = st.file_uploader("Sube tu archivo CSV para visualizar los datos", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo CSV cargado exitosamente.")

            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df.set_index('fecha', inplace=True)
                st.info("Columna 'fecha' detectada y establecida como índice de tiempo.")

            st.session_state.df_cargado = df
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error al leer el archivo CSV: {e}")

    df_actual = st.session_state.get('df_cargado', None)

    if df_actual is not None:
        numeric_df = df_actual.select_dtypes(include=['number'])

        st.subheader("📈 Gráfico de Líneas (Serie de Tiempo)")
        st.line_chart(df_actual)

        st.subheader("📊 Matriz de Correlación")
        try:
            numeric_df_clean = df_actual.select_dtypes(include=['number']).dropna(axis=1, how='any')
            if numeric_df_clean.shape[1] >= 2:
                corr_matrix = numeric_df_clean.corr()
                fig = px.imshow(corr_matrix, text_auto=True, title="Matriz de Correlación")
                st.plotly_chart(fig)
            else:
                st.warning("Se necesitan al menos dos columnas numéricas sin valores faltantes para la matriz de correlación.")
        except Exception as e:
            st.warning(f"No se pudo generar la matriz de correlación: {e}")

        st.subheader("Gráfico de Caja (Boxplot)")
        columnas = numeric_df.columns.tolist()
        if columnas:
            col_selec = st.selectbox("Selecciona una columna para boxplot", columnas)
            fig_box = px.box(numeric_df, y=col_selec)
            st.plotly_chart(fig_box)

        st.subheader("Gráfico de Barras Agrupado")
        if len(columnas) >= 2:
            x = st.selectbox("Columna X", columnas, key="bar_x")
            y = st.selectbox("Columna Y", columnas, key="bar_y")
            fig_bar = px.bar(df_actual, x=x, y=y, color=x)
            st.plotly_chart(fig_bar)

        st.subheader("📄 Exportar Reportes")
        pdf_data = generar_pdf(df_actual)
        word_data = generar_word(df_actual)

        st.download_button("Descargar PDF", data=pdf_data, file_name="reporte.pdf", mime="application/pdf")
        st.download_button("Descargar Word", data=word_data, file_name="reporte.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    if st.button("Cerrar sesión"):
        logout()

# ----------------- Panel del Técnico -----------------
def tecnico_panel():
    st.title("Hydromet - Panel del Técnico")
    st.write(f"Bienvenido, {st.session_state.usuario}")

    uploaded_file = st.file_uploader("Sube archivo CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df.set_index('fecha', inplace=True)
            st.session_state.df_cargado = df
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")

    df_actual = st.session_state.get('df_cargado', None)
    if df_actual is not None:
        st.line_chart(df_actual)
        st.download_button("Descargar PDF", data=generar_pdf(df_actual), file_name="reporte.pdf", mime="application/pdf")
        st.download_button("Descargar Word", data=generar_word(df_actual), file_name="reporte.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    if st.button("Cerrar sesión"):
        logout()

# ----------------- Inicialización -----------------
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.df_cargado = None

# ----------------- Main -----------------
def main():
    if st.session_state.autenticado:
        if st.session_state.usuario == "admin":
            admin_panel()
        else:
            tecnico_panel()
    else:
        login()

main()
    
