import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# --- Configurar la página ---
st.set_page_config(page_title="HydroClima PRO", layout="wide")

# --- Diccionario de usuarios ---
users = {
    "admin": {"password": "admin123", "role": "Administrador"},
    "supervisor": {"password": "super123", "role": "Supervisor"},
    "operador": {"password": "op123", "role": "Operador"},
}

# --- Manejo de sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.session_state.role = ""

# --- Login ---
if not st.session_state.logged_in:
    st.title("🌐 HydroClima PRO")
    st.subheader("Inicio de sesión")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = users[username]["role"]
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- Bienvenida ---
st.sidebar.title("Panel de Usuario")
st.sidebar.success(f"Bienvenido, {st.session_state.user} ({st.session_state.role})")
st.sidebar.markdown("Cierra sesión para cambiar de cuenta.")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.logged_in = False
    st.experimental_rerun()

# --- Cargar archivo CSV ---
st.title("📁 Cargar datos meteorológicos")
uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Archivo cargado correctamente.")
        st.dataframe(df)

        st.markdown("---")
        st.subheader("📊 Visualización de datos")

        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        if not numeric_columns:
            st.warning("El archivo no contiene columnas numéricas.")
        else:
            col = st.selectbox("Selecciona una columna para graficar", numeric_columns)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines+markers', line=dict(color='aqua')))
            fig.update_layout(
                title=f"Visualización de {col}",
                template="plotly_dark",
                margin=dict(l=40, r=40, t=40, b=40),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- Funciones Pro ---
        st.markdown("---")
        st.subheader("📈 Funciones estadísticas PRO")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Media", round(df[col].mean(), 2))
            st.metric("Máximo", round(df[col].max(), 2))
            st.metric("Mínimo", round(df[col].min(), 2))
        with col2:
            st.metric("Desviación estándar", round(df[col].std(), 2))
            st.metric("Mediana", round(df[col].median(), 2))
            st.metric("Moda", df[col].mode()[0] if not df[col].mode().empty else "N/A")

        # --- Exportar informes ---
        st.markdown("---")
        st.subheader("📝 Exportar informe")

        comentario = st.text_area("Resumen o comentario del informe")
        col3, col4 = st.columns(2)

        # DOCX
        def export_to_word():
            doc = Document()
            doc.add_heading("Informe Hidrometeorológico", 0)
            doc.add_paragraph(f"Generado por: {st.session_state.user} ({st.session_state.role})")
            doc.add_paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            doc.add_paragraph(f"Comentario: {comentario}")
            doc.add_paragraph("Datos:")
            table = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = table.rows[0].cells
            for i, col_name in enumerate(df.columns):
                hdr_cells[i].text = col_name
            for i in range(min(50, len(df))):
                row_cells = table.add_row().cells
                for j, value in enumerate(df.iloc[i]):
                    row_cells[j].text = str(value)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer

        with col3:
            if st.button("📤 Descargar Word"):
                word_buffer = export_to_word()
                st.download_button(
                    label="Descargar DOCX",
                    data=word_buffer,
                    file_name="informe.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        # PDF
        def export_to_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe Hidrometeorológico", ln=True, align='C')
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt=f"Usuario: {st.session_state.user} ({st.session_state.role})\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\nComentario: {comentario}")
            pdf.ln(5)
            for i in range(min(50, len(df))):
                row = ", ".join([f"{val}" for val in df.iloc[i].values])
                pdf.multi_cell(0, 10, row)
            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            return pdf_buffer

        with col4:
            if st.button("📥 Descargar PDF"):
                pdf_file = export_to_pdf()
                st.download_button(
                    label="Descargar PDF",
                    data=pdf_file,
                    file_name="informe.pdf",
                    mime="application/pdf"
                )

        # --- Opciones especiales para ADMIN ---
        if st.session_state.role == "Administrador":
            st.markdown("---")
            st.subheader("⚙️ Herramientas avanzadas (solo admin)")
            st.markdown("- Conexión directa a medidores (simulada)")
            st.markdown("- Configuración global del sistema")
            st.markdown("- Monitoreo en tiempo real (próximamente)")
            st.info("Estas funciones estarán activas en la próxima versión Pro extendida.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, carga un archivo CSV para comenzar.")
