import streamlit as st import pandas as pd import numpy as np import plotly.express as px import plotly.graph_objects as go from io import BytesIO from docx import Document from fpdf import FPDF from datetime import datetime

--- Autenticación ---

USERS = { "admin": {"password": "admin123", "role": "admin"}, "tecnico": {"password": "tecnico123", "role": "tecnico"}, "visualizador": {"password": "visual123", "role": "visualizador"} }

if "authenticated" not in st.session_state: st.session_state.authenticated = False st.session_state.username = "" st.session_state.role = ""

def login(): st.title("Inicio de Sesión") username = st.text_input("Usuario") password = st.text_input("Contraseña", type="password") if st.button("Iniciar sesión"): user = USERS.get(username) if user and user["password"] == password: st.session_state.authenticated = True st.session_state.username = username st.session_state.role = user["role"] st.experimental_rerun() else: st.error("Credenciales inválidas")

def logout(): st.session_state.authenticated = False st.session_state.username = "" st.session_state.role = "" st.experimental_rerun()

--- Exportar PDF ---

def export_pdf(df): try: pdf = FPDF() pdf.add_page() pdf.set_font("Arial", size=12) pdf.cell(200, 10, txt="Informe de Datos", ln=True, align="C") pdf.ln()

for col in df.columns:
        pdf.cell(40, 10, txt=str(col), border=1)
    pdf.ln()

    for i in range(min(len(df), 20)):
        for col in df.columns:
            pdf.cell(40, 10, txt=str(df.iloc[i][col]), border=1)
        pdf.ln()

    output = BytesIO()
    pdf.output(output)
    st.download_button("Descargar PDF", data=output.getvalue(), file_name="informe.pdf")
except Exception as e:
    st.error(f"Error al generar PDF: {e}")

--- Exportar Word ---

def export_word(df): try: doc = Document() doc.add_heading("Informe de Datos", 0) table = doc.add_table(rows=1, cols=len(df.columns)) hdr_cells = table.rows[0].cells for i, col in enumerate(df.columns): hdr_cells[i].text = str(col)

for i in range(min(len(df), 20)):
        row_cells = table.add_row().cells
        for j, col in enumerate(df.columns):
            row_cells[j].text = str(df.iloc[i][col])

    output = BytesIO()
    doc.save(output)
    st.download_button("Descargar Word", data=output.getvalue(), file_name="informe.docx")
except Exception as e:
    st.error(f"Error al generar Word: {e}")

--- Panel Administrador ---

def admin_panel(): st.title("Panel de Control del Administrador")

file = st.file_uploader("Sube un archivo CSV", type="csv")
if file:
    df = pd.read_csv(file)
    st.dataframe(df)

    # --- Herramientas del Admin ---
    st.subheader("1. Exportar Informes")
    export_pdf(df)
    export_word(df)

    st.subheader("2. Estadísticas Básicas")
    st.write(df.describe())

    st.subheader("3. Histograma")
    col = st.selectbox("Selecciona columna para histograma", df.select_dtypes(include=[np.number]).columns)
    st.plotly_chart(px.histogram(df, x=col, nbins=20))

    st.subheader("4. Gráfico de Líneas")
    st.plotly_chart(px.line(df))

    st.subheader("5. Mapa de Calor (Correlación)")
    numeric_df = df.select_dtypes(include=[np.number])
    fig_corr = px.imshow(numeric_df.corr(), text_auto=True)
    st.plotly_chart(fig_corr)

    st.subheader("6. Dispersión")
    if len(numeric_df.columns) >= 2:
        x_col = st.selectbox("X", numeric_df.columns)
        y_col = st.selectbox("Y", numeric_df.columns[::-1])
        st.plotly_chart(px.scatter(df, x=x_col, y=y_col))

    st.subheader("7. Boxplot")
    st.plotly_chart(px.box(df, y=col))

    st.subheader("8. Valores Nulos")
    st.write(df.isnull().sum())

    st.subheader("9. Medición en Tiempo Real")
    realtime = {"sensor_1": np.random.rand(), "sensor_2": np.random.rand()*10}
    st.write(realtime)

    st.subheader("10. Alerta por Límites")
    lim_col = st.selectbox("Columna a monitorear", numeric_df.columns, key="limite")
    lim_val = st.number_input("Valor límite", value=100.0)
    if any(df[lim_col] > lim_val):
        st.warning(f"¡Valores mayores a {lim_val} detectados!")

    st.subheader("11. Personalización de Gráficos")
    st.plotly_chart(go.Figure(data=[go.Scatter(y=df[lim_col], mode='lines+markers')]))

    st.subheader("12. Promedios por Día")
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"])
        st.write(df.groupby(df["fecha"].dt.date).mean())

    st.subheader("13. Descargar CSV Limpio")
    st.download_button("Descargar CSV", df.to_csv(index=False), file_name="datos_limpios.csv")

    st.subheader("14. Informe General")
    st.write("Datos procesados, alertas y estadísticas resumidas.")

    st.subheader("15. Monitoreo Sensorial Simulado")
    st.line_chart(np.random.randn(100, 2))

st.button("Cerrar sesión", on_click=logout)

--- App Principal ---

if not st.session_state.authenticated: login() else: if st.session_state.role == "admin": admin_panel() else: st.warning("Usuario con permisos limitados. Esta versión es solo para administradores.") st.button("Cerrar sesión", on_click=logout)

