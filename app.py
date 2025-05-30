import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from docx import Document
from fpdf import FPDF
from datetime import datetime

# --- Simulación de base de datos de usuarios ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "tecnico": {"password": "tec123", "role": "tecnico"},
    "user": {"password": "user123", "role": "viewer"}
}

st.set_page_config(page_title="Panel Hidromet", layout="wide")

# --- Funciones auxiliares ---
def cargar_datos():
    archivo = st.file_uploader("📂 Cargar archivo de datos", type=["csv"])
    if archivo:
        try:
            df = pd.read_csv(archivo)
            st.session_state.df = df
            st.success("✅ Archivo cargado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al cargar el archivo: {e}")


def exportar_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe Hidromet", ln=True, align="C")
        pdf.cell(200, 10, txt=datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True, align="C")

        for i in range(len(df)):
            fila = ', '.join([str(x) for x in df.iloc[i]])
            pdf.multi_cell(0, 10, fila)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        st.download_button(
            label="📥 Descargar PDF",
            data=buffer,
            file_name="informe.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")


def exportar_word(df):
    try:
        doc = Document()
        doc.add_heading("Informe Hidromet", 0)

        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)

        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        st.download_button("📥 Descargar Word", buffer, file_name="informe.docx")
    except Exception as e:
        st.error(f"Error al generar Word: {e}")


def graficos_avanzados(df):
    st.subheader("📊 Análisis de Datos")
    if df.empty:
        st.warning("Por favor, cargue un archivo para mostrar datos.")
        return

    columnas_numericas = df.select_dtypes(include=np.number).columns.tolist()
    if not columnas_numericas:
        st.error("El archivo no contiene columnas numéricas.")
        return

    st.plotly_chart(px.line(df, x=df.index, y=columnas_numericas, title="Tendencia Temporal"))
    st.plotly_chart(px.histogram(df, x=columnas_numericas[0], title="Distribución de " + columnas_numericas[0]))
    st.plotly_chart(px.imshow(df[columnas_numericas].corr(), text_auto=True, aspect="auto", title="Mapa de Correlación"))


def admin_panel():
    st.title("📡 Panel de Administrador - Control Total")
    df = st.session_state.get("df", pd.DataFrame())

    cargar_datos()

    st.markdown("---")
    st.header("📋 Datos Cargados")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        exportar_pdf(df)
        exportar_word(df)
        graficos_avanzados(df)

        st.markdown("---")
        st.header("🔧 Herramientas Avanzadas")
        with st.expander("1. Conexión en Tiempo Real con Equipos"):
            st.info("[Simulado] Obteniendo datos desde sensores...")

        with st.expander("2. Análisis de Calidad del Agua"):
            st.success("[Simulado] Niveles de pH, turbidez y oxígeno dentro de rango.")

        with st.expander("3. Predicción con IA"):
            st.warning("[Simulado] Modelo predice aumento de caudal en 48h")

        with st.expander("4. Comparativa Histórica"):
            st.plotly_chart(px.box(df, y=columnas_numericas, title="Comparativa Histórica"))

        with st.expander("5. Exportación Avanzada"):
            st.download_button("⬇ Exportar CSV", df.to_csv(index=False), file_name="datos.csv")

        with st.expander("6. Monitoreo en Vivo"):
            st.info("[Simulado] Datos actualizados cada 60 segundos")

        with st.expander("7. Alertas Configurables"):
            st.warning("[Simulado] Alerta de caudal crítico activada")

        with st.expander("8. Reportes Automáticos por Email"):
            st.success("[Simulado] Informe enviado a administracion@empresa.com")

        with st.expander("9. Integración con API de sensores"):
            st.info("[Simulado] API conectada con éxito")

        with st.expander("10. Estadísticas Avanzadas"):
            st.write(df.describe())

        with st.expander("11. Mapa Geográfico de Sensores"):
            st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"}), zoom=4)

        with st.expander("12. Configuración de Umbrales"):
            st.slider("Umbral de alerta de caudal", 0, 1000, 300)

        with st.expander("13. Vista Personalizada de Variables"):
            st.multiselect("Seleccionar variables", df.columns.tolist(), default=columnas_numericas[:3])

        with st.expander("14. Panel de Logs"):
            st.code("[10:00] Sensor A activo\n[10:01] Datos recibidos correctamente")

        with st.expander("15. Dashboard Diario"):
            st.success("[Simulado] Dashboard generado y archivado")
    else:
        st.info("Por favor cargue un archivo para acceder a las herramientas.")


def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.form("login_form"):
            st.subheader("🔐 Iniciar sesión")
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar sesión")

            if submitted:
                user = USERS.get(username)
                if user and user["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.session_state.role = user["role"]
                    st.success(f"Login exitoso. Bienvenido, {username}")
                    st.experimental_set_query_params(refresh=str(datetime.now()))
                    st.stop()
                else:
                    st.error("Credenciales inválidas")
    else:
        if st.button("Cerrar sesión"):
            for key in ["authenticated", "user", "role", "df"]:
                st.session_state.pop(key, None)
            st.success("Sesión cerrada")
            st.experimental_set_query_params(refresh=str(datetime.now()))
            st.stop()


# --- Main ---
if __name__ == "__main__":
    login()
    if st.session_state.get("authenticated"):
        if st.session_state.get("role") == "admin":
            admin_panel()
        else:
            st.error("Acceso restringido. Este panel es solo para administradores.")
        
