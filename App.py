import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from docx import Document
from datetime import datetime

# ----------------- CONFIGURACIÓN DE LA APP -----------------
st.set_page_config(
    page_title="Hydromet Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💧"
)

# ----------------- DATOS DE USUARIO -----------------
USUARIOS = {
    "admin": "YZ1BKzgHIK7P7ZrB",
    "tecnico": "tecnico123"
}

# ----------------- LOGIN -----------------
def login():
    with st.container():
        st.markdown("### 💧 Hydromet App - Centro de Datos Ambientales")
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario")
            contraseña = st.text_input("🔒 Contraseña", type="password")
            login_btn = st.form_submit_button("Iniciar sesión")
            if login_btn:
                if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario
                    st.success(f"Bienvenido, {usuario}")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

# ----------------- CARGA DE DATOS -----------------
def cargar_datos():
    uploaded_file = st.file_uploader("📁 Cargar archivo CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])
                df.set_index('fecha', inplace=True)
            st.session_state.df_cargado = df
            st.success("Datos cargados correctamente")
        except Exception as e:
            st.error(f"Error al cargar archivo: {e}")

# ----------------- EXPORTACIÓN -----------------
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

# ----------------- PÁGINA PRINCIPAL -----------------
def main_panel():
    with st.sidebar:
        st.markdown("## 🌐 Navegación")
        st.button("Cerrar sesión", on_click=logout)
        st.markdown("---")
        cargar_datos()

    df = st.session_state.get('df_cargado')
    if df is not None:
        st.title("📊 Panel de Datos Ambientales")
        tab1, tab2, tab3 = st.tabs(["🔍 Vista previa", "📈 Gráficas", "📤 Exportar"])

        with tab1:
            st.subheader("Vista previa del dataset")
            st.dataframe(df, use_container_width=True)
            st.metric("Total de registros", len(df))

        with tab2:
            numeric_df = df.select_dtypes(include='number')
            if not numeric_df.empty:
                st.subheader("Gráfica de Línea")
                st.line_chart(numeric_df)

                st.subheader("Matriz de Correlación")
                fig = px.imshow(numeric_df.corr(), text_auto=True)
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Dispersión Personalizada")
                cols = numeric_df.columns.tolist()
                col1, col2 = st.columns(2)
                with col1:
                    x = st.selectbox("Eje X", cols)
                with col2:
                    y = st.selectbox("Eje Y", cols)
                if x and y:
                    fig_scatter = px.scatter(df, x=x, y=y)
                    st.plotly_chart(fig_scatter)

        with tab3:
            st.subheader("Exportar Reportes")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📄 Descargar PDF", data=generar_pdf(df), file_name="reporte.pdf", mime="application/pdf")
            with col2:
                st.download_button("📝 Descargar Word", data=generar_word(df), file_name="reporte.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    else:
        st.info("Carga un archivo CSV para comenzar el análisis.")

# ----------------- LOGOUT -----------------
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.df_cargado = None
    st.rerun()

# ----------------- INICIALIZACIÓN -----------------
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = ""
if 'df_cargado' not in st.session_state:
    st.session_state.df_cargado = None

# ----------------- MAIN -----------------
if st.session_state.autenticado:
    main_panel()
else:
    login()
                             
