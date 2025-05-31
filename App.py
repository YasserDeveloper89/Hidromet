import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
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
    for _, row in df_to_export.iterrows():
        row_cells = table.add_row().cells
        for i, col_name in enumerate(df_to_export.columns):
            row_cells[i].text = str(row[col_name])
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ----------------- Panel Principal -----------------
def admin_panel():
    st.title("Hydromet - Panel")
    st.write(f"Bienvenido, {st.session_state.usuario}")

    st.subheader("📁 Cargar Datos (CSV)")
    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])
                df.set_index('fecha', inplace=True)
                st.info("Columna 'fecha' establecida como índice.")
            st.session_state.df_cargado = df
            st.success("Archivo CSV cargado.")
        except Exception as e:
            st.error(f"Error al cargar archivo: {e}")

    df_actual = st.session_state.get('df_cargado')
    if df_actual is not None:
        st.subheader("Vista previa")
        st.dataframe(df_actual)

        st.subheader("🔢 Gráfico de Línea")
        st.line_chart(df_actual)

        columnas_numericas = df_actual.select_dtypes(include=['number']).columns.tolist()
        if columnas_numericas:
            hist_col = st.selectbox("Selecciona columna para histograma", columnas_numericas)
            st.plotly_chart(px.histogram(df_actual, x=hist_col, marginal="rug"))

        if st.session_state.usuario == "admin":
            st.subheader("Matriz de Correlación")
            try:
                fig = px.imshow(df_actual.corr(), text_auto=True)
                st.plotly_chart(fig)
            except Exception as e:
                st.warning(f"No se pudo generar la matriz de correlación: {e}")

            if len(columnas_numericas) >= 2:
                x = st.selectbox("Eje X", columnas_numericas, key="x")
                y = st.selectbox("Eje Y", columnas_numericas, key="y")
                st.plotly_chart(px.scatter(df_actual, x=x, y=y))

        st.subheader("Exportar")
        st.download_button("📄 PDF", data=generar_pdf(df_actual), file_name="reporte.pdf", mime="application/pdf")
        st.download_button("📝 Word", data=generar_word(df_actual), file_name="reporte.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

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
            
