import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document
from datetime import datetime # Import for the new temperature feature

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

    # Add table headers
    # Ensure all columns are handled
    col_widths = [pdf.w / (len(df_to_export.columns) + 1)] * len(df_to_export.columns) # Adjust as needed
    
    # Try to fit content, simple fixed width for now
    for col in df_to_export.columns:
        pdf.cell(40, 10, str(col), border=1) # Fixed width, adjust if cols are too wide
    pdf.ln()

    for index, row in df_to_export.iterrows():
        # This part handles the index if it's a Timestamp, otherwise just print it.
        # However, for the PDF generation based on df_to_export, typically you'd just iterate through rows.
        # Assuming df_to_export is just the data. If index needs to be a column, it should be in df_to_export.
        
        # Iterating through row items directly
        for item in row:
            pdf.cell(40, 10, str(item), border=1) # Fixed width
        pdf.ln()

    buffer = BytesIO()
    pdf.output(buffer, 'S')
    pdf_data = buffer.getvalue()
    return pdf_data

# ----------------- Generar Word -----------------
def generar_word(df_to_export):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    table = doc.add_table(rows=1, cols=len(df_to_export.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df_to_export.columns):
        hdr_cells[i].text = col
    for index, row in df_to_export.iterrows():
        row_cells = table.add_row().cells
        for i, col_name in enumerate(df_to_export.columns):
            row_cells[i].text = str(row[col_name])
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ----------------- Panel de Administración -----------------
def admin_panel():
    st.title("🛠️ Panel de Administración")
    st.write(f"Bienvenido, {st.session_state.usuario}")

    # --- CSV Upload Section ---
    st.subheader("📁 Cargar y Analizar Datos (CSV)")
    # This is the line that will remain, with clear instructions without repetition
    uploaded_file = st.file_uploader("Sube tu archivo CSV aquí para visualizar y analizar.", type=["csv"]) 

    # Initialize df_cargado if no file is uploaded
    if uploaded_file is None:
        st.session_state.df_cargado = None
    
    # Process uploaded file and set df_cargado
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo CSV cargado exitosamente.")

            # Attempt to set 'fecha' as index
            if 'fecha' in df.columns:
                try:
                    df['fecha'] = pd.to_datetime(df['fecha'])
                    df.set_index('fecha', inplace=True)
                    st.info("Columna 'fecha' detectada y establecida como índice de tiempo.")
                except Exception as e:
                    st.warning(f"No se pudo convertir la columna 'fecha' a formato de fecha/hora: {e}")
            elif st.checkbox("¿Tu archivo tiene una columna de fecha/hora para el índice?"):
                date_column = st.selectbox("Selecciona la columna de fecha/hora:", df.columns)
                if date_column:
                    try:
                        df[date_column] = pd.to_datetime(df[date_column])
                        df.set_index(date_column, inplace=True)
                        st.info(f"Columna '{date_column}' detectada y establecida como índice de tiempo.")
                    except Exception as e:
                        st.error(f"Error al convertir la columna '{date_column}' a formato de fecha/hora: {e}")
            
            st.subheader("Vista Previa de los Datos")
            st.dataframe(df)

            st.session_state.df_cargado = df

        except Exception as e:
            st.error(f"Error al leer el archivo CSV: {e}")
            st.info("Asegúrate de que el archivo es un CSV válido y no está dañado.")
            st.session_state.df_cargado = None
    
    # --- Conditional Display of CSV-related tools ---
    df_actual = st.session_state.df_cargado

    if df_actual is None: # If no CSV is loaded, show the initial prompt
        # THIS IS THE EXACT LINE THAT WAS REQUESTED TO BE REMOVED WHEN IT WAS DUPLICATED,
        # BUT IT'S APPROPRIATE TO SHOW HERE WHEN NO FILE IS YET UPLOADED.
        # Previous removal attempt was incorrect.
        st.info("Sube un archivo CSV para visualizar los datos, gráficos y opciones de exportación.")
    elif df_actual is not None and not df_actual.empty: # Only show these if a CSV is loaded
        numeric_df = df_actual.select_dtypes(include=['number'])

        if not numeric_df.empty:
            st.subheader("📈 Visualización de Datos (Series de Tiempo si hay índice de fecha)")
            st.line_chart(df_actual)

            st.subheader("📊 Gráfico de Correlación")
            try:
                fig = px.imshow(numeric_df.corr(), text_auto=True, title="Matriz de Correlación")
                st.plotly_chart(fig)
            except Exception as e:
                st.warning(f"No se pudo generar el gráfico de correlación. Asegúrate de tener al menos dos columnas numéricas. Error: {e}")

            st.subheader("Exploración de Gráficos (Dinámico)")
            columnas_numericas = df_actual.select_dtypes(include=['number']).columns.tolist()
            
            if len(columnas_numericas) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_axis = st.selectbox("Selecciona eje X (Scatter Plot):", options=columnas_numericas, key="scatter_x")
                with col2:
                    y_axis = st.selectbox("Selecciona eje Y (Scatter Plot):", options=columnas_numericas, key="scatter_y")
                if x_axis and y_axis:
                    try:
                        fig_scatter = px.scatter(df_actual, x=x_axis, y=y_axis, title=f"Dispersión de {x_axis} vs {y_axis}")
                        st.plotly_chart(fig_scatter)
                    except Exception as e:
                        st.warning(f"No se pudo generar el gráfico de dispersión: {e}")
            else:
                st.info("Necesitas al menos dos columnas numéricas para el gráfico de dispersión.")

            if columnas_numericas:
                hist_column = st.selectbox("Selecciona columna para Histograma:", options=columnas_numericas, key="hist_col")
                if hist_column:
                    try:
                        fig_hist = px.histogram(df_actual, x=hist_column, marginal="rug", title=f"Distribución de {hist_column}")
                        st.plotly_chart(fig_hist)
                    except Exception as e:
                        st.warning(f"No se pudo generar el histograma: {e}")
            else:
                st.info("No hay columnas numéricas para generar histogramas.")

        else:
            st.warning("El DataFrame cargado no contiene columnas numéricas para generar gráficos.")

        st.subheader("📤 Exportar Datos")
        pdf_data = generar_pdf(df_actual)
        word_data = generar_word(df_actual)

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
    
    ---

    # --- Nueva Herramienta: Visualización de Temperatura y Fecha (Siempre visible) ---
    st.subheader("🌡️ Visualización de Datos de Temperatura y Ambiente")
    st.write("Aquí puedes monitorear de manera clara e intuitiva datos ambientales clave como la temperatura y la fecha.")

    # Simulated data for demonstration
    # In a real application, this would come from sensors or a database
    temp_data = {
        "Fecha": [datetime(2025, 5, 29, 10, 0), datetime(2025, 5, 29, 11, 0), datetime(2025, 5, 29, 12, 0), datetime(2025, 5, 29, 13, 0), datetime(2025, 5, 29, 14, 0), datetime(2025, 5, 29, 15, 0)],
        "Temperatura (°C)": [22.5, 23.1, 24.0, 23.8, 22.9, 23.5],
        "Humedad (%)": [60, 58, 55, 57, 61, 62],
        "Presión (hPa)": [1012, 1011, 1010, 1010, 1011, 1012]
    }
    temp_df = pd.DataFrame(temp_data)
    temp_df['Fecha'] = pd.to_datetime(temp_df['Fecha']) # Ensure 'Fecha' is datetime

    if not temp_df.empty:
        col_temp1, col_temp2, col_temp3 = st.columns(3)
        
        with col_temp1:
            latest_temp = temp_df["Temperatura (°C)"].iloc[-1]
            # You could add a delta calculation if you had previous data points
            st.metric(label="Temperatura Actual", value=f"{latest_temp}°C", delta="0.5°C") # Example delta
        
        with col_temp2:
            latest_humidity = temp_df["Humedad (%)"].iloc[-1]
            st.metric(label="Humedad Actual", value=f"{latest_humidity}%", delta="-2%") # Example delta
        
        with col_temp3:
            latest_date_time = temp_df["Fecha"].iloc[-1].strftime("%Y-%m-%d %H:%M:%S")
            st.metric(label="Última Actualización", value=latest_date_time)

        st.write("#### Tendencia de Temperatura a lo largo del tiempo")
        fig_temp_trend = px.line(temp_df, x="Fecha", y="Temperatura (°C)", title="Histórico de Temperatura")
        st.plotly_chart(fig_temp_trend, use_container_width=True)

        st.write("#### Datos Ambientales Detallados")
        st.dataframe(temp_df) # Display the full DataFrame for more details
    else:
        st.info("No hay datos ambientales disponibles para mostrar en este momento.")

    ---

    # --- Otras herramientas de administración (ejemplo) ---
    st.subheader("👥 Gestión de Usuarios (Próximamente)")
    st.info("Esta sección estará disponible en futuras actualizaciones para gestionar usuarios y permisos.")

    ---

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
    
