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
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Datos", ln=True, align="C")
    pdf.ln()
    col_width = pdf.w / (len(df.columns) + 1)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()
    for index, row in df.iterrows():
        pdf.cell(col_width, 10, str(index), border=1)
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# ----------------- Generar Word -----------------
def generar_word(df):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ----------------- Panel Principal -----------------
def admin_panel():
    st.title("🛠️ Hydromet - Panel de Administración")
    st.write(f"Bienvenido, {st.session_state.usuario}")
    
    uploaded_file = st.file_uploader("Sube tu archivo CSV para visualizar los datos", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df.set_index('fecha', inplace=True)
            st.session_state.df = df
        except Exception as e:
            st.error(f"Error al cargar CSV: {e}")
            return
    
    df = st.session_state.get("df")
    if df is None:
        return

    st.subheader("📃 Vista previa")
    st.dataframe(df)

    st.subheader("📈 Gráfico de Línea")
    st.line_chart(df)

    st.subheader("📊 Matriz de Correlación")
    try:
        numeric_df = df.select_dtypes(include='number')
        fig = px.imshow(numeric_df.corr(), text_auto=True, title="Matriz de Correlación")
        st.plotly_chart(fig)
    except Exception as e:
        st.warning(f"No se pudo generar la matriz de correlación: {e}")

    st.subheader("Gráfico de Barras")
    column = st.selectbox("Selecciona columna para barras:", df.select_dtypes(include='number').columns)
    st.bar_chart(df[column])

    st.subheader("Boxplot (Diagrama de caja)")
    st.plotly_chart(px.box(df, y=column, title=f"Boxplot de {column}"))

    st.subheader("📄 Exportar")
    st.download_button("Descargar PDF", generar_pdf(df), file_name="reporte.pdf", mime="application/pdf")
    st.download_button("Descargar Word", generar_word(df), file_name="reporte.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.button("Cerrar sesión", on_click=logout)

def tecnico_panel():
    st.title("Hydromet - Panel Técnico")
    st.write(f"Bienvenido, {st.session_state.usuario}")

    uploaded_file = st.file_uploader("Sube tu archivo CSV para visualizar los datos", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df.set_index('fecha', inplace=True)
            st.session_state.df = df
        except Exception as e:
            st.error(f"Error al cargar CSV: {e}")
            return

    df = st.session_state.get("df")
    if df is None:
        return

    st.subheader("Vista previa")
    st.dataframe(df)

    st.subheader("Gráfico de Línea")
    st.line_chart(df)

    st.subheader("Exportar")
    st.download_button("Descargar PDF", generar_pdf(df), file_name="reporte.pdf", mime="application/pdf")
    st.download_button("Descargar Word", generar_word(df), file_name="reporte.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.button("Cerrar sesión", on_click=logout)

# ----------------- Inicialización -----------------
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""

# ----------------- Main -----------------
def main():
    if not st.session_state.autenticado:
        login()
    elif st.session_state.usuario == "admin":
        admin_panel()
    else:
        tecnico_panel()

main()
    
