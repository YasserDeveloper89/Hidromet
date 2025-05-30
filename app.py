import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from docx import Document
from fpdf import FPDF
import plotly.graph_objects as go
import seaborn as sns
from datetime import datetime

# --- Configuración inicial ---
st.set_page_config(page_title="HydroClimaPRO", layout="wide")

# --- Base de usuarios (en producción usar DB) ---
users = {
    "admin": {"password": "admin123", "role": "Administrador"},
    "supervisor": {"password": "super2024", "role": "Supervisor"},
    "tecnico": {"password": "tec2024", "role": "Técnico"},
}

# --- Variables de sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.user = ""

# --- Login ---
if not st.session_state.logged_in:
    st.title("🔐 Iniciar sesión - HydroClimaPRO")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = users[username]["role"]
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")

# --- App Principal ---
else:
    st.sidebar.success(f"Usuario: {st.session_state.user} ({st.session_state.role})")
    st.sidebar.button("Cerrar sesión", on_click=lambda: st.session_state.update({"logged_in": False, "user": "", "role": ""}))

    st.title("📊 HydroClimaPRO - Análisis Hidrometeorológico")

    # --- Carga de archivo ---
    uploaded_file = st.file_uploader("📁 Cargar archivo CSV", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo cargado correctamente.")
            st.dataframe(df)

            # --- Visualización avanzada ---
            st.subheader("📈 Visualización de Datos")
            col = st.selectbox("Selecciona la columna a graficar", df.select_dtypes(include=np.number).columns)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode="lines+markers", line=dict(color="cyan")))
            fig.update_layout(template="plotly_dark", title=f"Variación de {col}", xaxis_title="Índice", yaxis_title=col)
            st.plotly_chart(fig, use_container_width=True)

            # --- Exportar Informe ---
            st.subheader("📝 Generar Informe")
            informe_texto = st.text_area("Resumen del Informe", "El presente informe contiene los análisis climáticos...")
            nombre_archivo = f"Informe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Informe Hidrometeorológico", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 10, informe_texto)
            pdf.ln(5)
            for col in df.columns:
                pdf.cell(0, 10, f"{col}: {df[col].mean():.2f}", ln=True)
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)
            st.download_button("📄 Descargar PDF", data=pdf_output, file_name=f"{nombre_archivo}.pdf", mime="application/pdf")

            # Word
            doc = Document()
            doc.add_heading("Informe Hidrometeorológico", level=1)
            doc.add_paragraph(informe_texto)
            doc.add_heading("Resumen de Datos", level=2)
            for col in df.columns:
                doc.add_paragraph(f"{col}: {df[col].mean():.2f}")
            word_output = BytesIO()
            doc.save(word_output)
            word_output.seek(0)
            st.download_button("📝 Descargar Word", data=word_output, file_name=f"{nombre_archivo}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            # --- Funciones Exclusivas Administrador ---
            if st.session_state.role == "Administrador":
                st.subheader("🛠️ Herramientas Avanzadas (Admin)")
                st.markdown("- 🔌 **Conexión a Sensores (Simulado)**")
                st.markdown("- 🧠 **Modelado predictivo con IA (pendiente)**")
                st.markdown("- 🗃️ **Gestión de datos históricos**")
                st.markdown("- ⚙️ **Configuración global del sistema**")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        st.info("Por favor, carga un archivo CSV para comenzar.")
