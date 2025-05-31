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
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
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

    if uploaded_file is None:
        st.session_state.df_cargado = None
        st.info("Por favor, sube un archivo CSV válido para comenzar.")
        return

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
        return

    df_actual = st.session_state.df_cargado

    if df_actual is not None and not df_actual.empty:
        numeric_df = df_actual.select_dtypes(include=['number'])

        st.subheader("📈 Visualización de Datos")
        st.line_chart(df_actual)

        st.subheader("📊 Matriz de Correlación")
        try:
            corr_df = numeric_df.corr()
            fig = px.imshow(corr_df, text_auto=True, title="Matriz de Correlación")
            st.plotly_chart(fig)
        except Exception as e:
            st.warning(f"No se pudo generar la matriz de correlación: {e}")

        st.subheader("Gráfico de Dispersión")
        columnas_numericas = numeric_df.columns.tolist()
        if len(columnas_numericas) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                x_axis = st.selectbox("Eje X:", columnas_numericas)
            with col2:
                y_axis = st.selectbox("Eje Y:", columnas_numericas)
            try:
                fig_scatter = px.scatter(df_actual, x=x_axis, y=y_axis, title=f"Dispersión de {x_axis} vs {y_axis}")
                st.plotly_chart(fig_scatter)
            except Exception as e:
                st.warning(f"No se pudo generar el gráfico: {e}")

        st.subheader("Histograma")
        hist_col = st.selectbox("Selecciona columna para histograma:", columnas_numericas)
        try:
            fig_hist = px.histogram(df_actual, x=hist_col, title=f"Histograma de {hist_col}")
            st.plotly_chart(fig_hist)
        except Exception as e:
            st.warning(f"No se pudo generar el histograma: {e}")

        # Exportar
        st.subheader("📄 Exportar Datos")
        pdf_data = generar_pdf(df_actual)
        word_data = generar_word(df_actual)

        st.download_button("Descargar PDF", data=pdf_data, file_name="reporte.pdf", mime="application/pdf")
        st.download_button("Descargar Word", data=word_data, file_name="reporte.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    if st.button("Cerrar sesión"):
        logout()

# ----------------- Inicialización -----------------
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""
if 'df_cargado' not in st.session_state:
    st.session_state.df_cargado = None

# ----------------- Main -----------------
def main():
    if st.session_state.autenticado:
        admin_panel()
    else:
        login()

main()
