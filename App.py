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
    st.title("🔐 Inicio de sesión")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.success(f"✅ Login exitoso. Bienvenido, {usuario}")
            # Eliminar st.query_params.update({"logged": "true"}) y st.experimental_rerun()
            # El cambio en st.session_state.autenticado hará que main() redibuje el panel de admin
        else:
            st.error("❌ Usuario o contraseña incorrectos")

# ----------------- Logout -----------------
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    # Eliminar st.query_params.clear() y st.experimental_rerun()
    # El cambio en st.session_state.autenticado hará que main() redibuje el formulario de login

# ----------------- Generar PDF -----------------
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Datos", ln=True, align="C")
    pdf.ln()
    # Ajustar el ancho de las celdas para que no se superpongan
    col_width = pdf.w / (len(df.columns) + 1) # +1 para el índice
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()
    for index, row in df.iterrows():
        pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d')), border=1) # Formatear la fecha
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()
    buffer = BytesIO()
    pdf.output(buffer)
    pdf_data = buffer.getvalue()
    return pdf_data

# ----------------- Generar Word -----------------
def generar_word(df):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for index, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, col in enumerate(df.columns):
            row_cells[i].text = str(row[col])
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ----------------- Panel de Administración -----------------
def admin_panel():
    st.title("🛠️ Panel de Administración")
    df = pd.DataFrame({
        "fecha": pd.to_datetime(pd.date_range(start="2023-01-01", periods=10)),
        "lluvia": [23, 12, 45, 67, 34, 22, 11, 56, 78, 21],
        "temperatura": [20, 21, 19, 18, 22, 23, 25, 24, 22, 21],
        "humedad": [60, 65, 63, 66, 62, 64, 67, 61, 59, 58]
    })
    df.set_index('fecha', inplace=True)

    st.subheader("📈 Visualización de Datos")
    st.line_chart(df)

    st.subheader("📊 Gráfico de Correlación")
    fig = px.imshow(df.corr(numeric_only=True), text_auto=True)
    st.plotly_chart(fig)

    st.subheader("📤 Exportar Datos")
    pdf_data = generar_pdf(df)
    word_data = generar_word(df)

    b64_pdf = base64.b64encode(pdf_data).decode()
    href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="reporte.pdf">📄 Descargar PDF</a>'
    st.markdown(href_pdf, unsafe_allow_html=True)

    b64_word = base64.b64encode(word_data).decode()
    href_word = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_word}" download="reporte.docx">📝 Descargar Word</a>'
    st.markdown(href_word, unsafe_allow_html=True)

    if st.button("Cerrar sesión"):
        logout()

# ----------------- Inicialización -----------------
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""

# ----------------- Main -----------------
def main():
    if st.session_state.autenticado:
        admin_panel()
    else:
        login()

main()
    
