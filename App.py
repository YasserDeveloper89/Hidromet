import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from docx import Document

# ----------------- Autenticación -----------------
USUARIOS = {
    "admin": "YZ1BKzgHIK7P7ZrB",
    "tecnico": "tecnico123"
}

# ----------------- Login -----------------
def login():
    st.title("💧 Hydromet - Centro de control de datos ambientales")
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
    st.session_state.df_cargado = None  # Limpiar datos al cerrar sesión
    st.rerun()

# ----------------- Exportar a PDF -----------------
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
    for row in df.itertuples(index=False):
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# ----------------- Exportar a Word -----------------
def generar_word(df):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for index, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, col_name in enumerate(df.columns):
            row_cells[i].text = str(row[col_name])
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ----------------- Cargar CSV -----------------
def cargar_datos():
    uploaded_file = st.file_uploader("📁 Cargar archivo CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])
                df.set_index('fecha', inplace=True)
                st.success("CSV cargado y columna 'fecha' establecida como índice.")
            st.session_state.df_cargado = df
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            st.session_state.df_cargado = None

# ----------------- Panel del Administrador -----------------
def admin_panel():
    st.title("🛠️ Panel de Administración")
    st.write(f"Bienvenido, {st.session_state.usuario}")
    cargar_datos()

    df = st.session_state.get('df_cargado')
    if df is not None:
        st.subheader("📄 Vista Previa de los Datos")
        st.dataframe(df)

        st.subheader("📈 Serie de Tiempo")
        st.line_chart(df)

        numeric_df = df.select_dtypes(include='number')
        if not numeric_df.empty:
            st.subheader("📊 Correlación")
            fig = px.imshow(numeric_df.corr(), text_auto=True, title="Matriz de Correlación")
            st.plotly_chart(fig)

            st.subheader("📌 Dispersión")
            cols = numeric_df.columns.tolist()
            x = st.selectbox("Eje X", cols)
            y = st.selectbox("Eje Y", cols)
            if x and y:
                fig_scatter = px.scatter(df, x=x, y=y, title=f"{x} vs {y}")
                st.plotly_chart(fig_scatter)

            st.subheader("📌 Histograma")
            col_hist = st.selectbox("Selecciona columna", cols)
            fig_hist = px.histogram(df, x=col_hist, marginal="rug", title=f"Histograma de {col_hist}")
            st.plotly_chart(fig_hist)

        st.subheader("📤 Exportar Datos")
        st.download_button("📄 Descargar PDF", data=generar_pdf(df), file_name="reporte.pdf", mime="application/pdf")
        st.download_button("📝 Descargar Word", data=generar_word(df), file_name="reporte.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    if st.button("Cerrar sesión"):
        logout()

# ----------------- Panel del Técnico -----------------
def tecnico_panel():
    st.title("🔧 Panel Técnico")
    st.write(f"Bienvenido, {st.session_state.usuario}")
    cargar_datos()

    df = st.session_state.get('df_cargado')
    if df is not None:
        st.subheader("📄 Vista Previa de los Datos")
        st.dataframe(df)

        st.subheader("📈 Serie de Tiempo")
        st.line_chart(df)

        numeric_df = df.select_dtypes(include='number')
        if not numeric_df.empty:
            st.subheader("📊 Correlación")
            fig = px.imshow(numeric_df.corr(), text_auto=True, title="Matriz de Correlación")
            st.plotly_chart(fig)

        st.subheader("📤 Exportar Datos")
        st.download_button("📄 Descargar PDF", data=generar_pdf(df), file_name="reporte.pdf", mime="application/pdf")
        st.download_button("📝 Descargar Word", data=generar_word(df), file_name="reporte.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.info("Carga un archivo CSV para comenzar.")

    if st.button("Cerrar sesión"):
        logout()

# ----------------- Inicialización -----------------
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = ""
if 'df_cargado' not in st.session_state:
    st.session_state.df_cargado = None

# ----------------- Main App -----------------
def main():
    if st.session_state.autenticado:
        if st.session_state.usuario == "admin":
            admin_panel()
        elif st.session_state.usuario == "tecnico":
            tecnico_panel()
    else:
        login()

main()
