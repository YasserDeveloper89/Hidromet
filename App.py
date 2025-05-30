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
            # Forzar una re-ejecución para que main() cargue admin_panel()
            st.rerun() # O st.experimental_rerun() si st.rerun() no funciona en tu versión
        else:
            st.error("❌ Usuario o contraseña incorrectos")

# ----------------- Logout -----------------
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    # Forzar una re-ejecución para que main() cargue el login nuevamente
    st.rerun() # O st.experimental_rerun() si st.rerun() no funciona en tu versión

# ----------------- Generar PDF -----------------
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Datos", ln=True, align="C")
    pdf.ln()

    # Añadir encabezados de la tabla al PDF
    # Asegúrate de que el ancho de la columna sea suficiente para los encabezados y datos
    col_width = pdf.w / (len(df.columns) + 1) # +1 para el índice
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()

    # Añadir filas de datos al PDF
    for index, row in df.iterrows():
        # Formatear la fecha para el índice si es un Timestamp
        if isinstance(index, pd.Timestamp):
            pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d')), border=1)
        else:
            pdf.cell(col_width, 10, str(index), border=1) # Para otros tipos de índice
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    buffer = BytesIO()
    # CAMBIO CRÍTICO: 'output' para escribir al buffer directamente
    pdf.output(buffer, 'S') # 'S' para cadena/bytes en memoria
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
    st.write(f"Bienvenido, {st.session_state.usuario}") # Para confirmar que el usuario está logeado

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

    st.subheader("📊 Gráfico de Dispersión (ejemplo de otra herramienta)")
    fig_scatter = px.scatter(df, x=df.index, y="temperatura", size="lluvia", color="humedad",
                             hover_name=df.index.strftime('%Y-%m-%d'))
    st.plotly_chart(fig_scatter)

    st.subheader("📊 Histograma de Lluvia (ejemplo de otra herramienta)")
    fig_hist = px.histogram(df, x="lluvia", marginal="rug", # rug adds a rug plot
                           hover_data=df.columns)
    st.plotly_chart(fig_hist)


    st.subheader("Tabla de Datos (ejemplo de otra herramienta)")
    st.dataframe(df) # Muestra la tabla de datos

    # Aquí puedes añadir más herramientas visuales o funcionales
    st.subheader("Otras Funcionalidades")
    st.info("Aquí irían otras herramientas o visualizaciones personalizadas.")

    st.subheader("📤 Exportar Datos")
    pdf_data = generar_pdf(df)
    word_data = generar_word(df)

    st.download_button(
        label="📄 Descargar PDF",
        data=pdf_data,
        file_name="reporte.pdf",
        mime="application/pdf"
    )

    st.download_button(
        label="📝 Descargar Word",
        data=word_data,
        file_name="reporte.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

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
