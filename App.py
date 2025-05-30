import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document
from docx.shared import Inches # Para ajustar tamaños en Word
from docx.enum.text import WD_ALIGN_PARAGRAPH # Para alinear texto en Word


# --- Configuración de la Página ---
st.set_page_config(
    page_title="App Hidrometeorológica Avanzada",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Autenticación -----------------
USUARIOS = {
    "admin": "admin123",
    "tecnico": "tecnico123"
}

# ----------------- Login -----------------
def login():
    st.title("🔐 Acceso a la Plataforma")
    st.markdown("---")

    col_login_img, col_login_form = st.columns([1, 1])

    with col_login_img:
        # --- USANDO IMAGEN LOCAL! ---
        # Asegúrate de que 'login_background.jpg' esté en la misma carpeta que App.py
        st.image("login_background.jpg",
                 caption="Monitoreo Inteligente del Clima", use_container_width=True)
        st.markdown("<p style='text-align: center; font-style: italic; color: grey;'>Una aplicación moderna para el análisis hidrometeorológico.</p>", unsafe_allow_html=True)


    with col_login_form:
        st.header("Por favor, inicia sesión")
        usuario = st.text_input("Usuario", help="Introduce tu nombre de usuario.")
        contraseña = st.text_input("Contraseña", type="password", help="Introduce tu contraseña.")
        
        if st.button("🚪 Iniciar sesión", use_container_width=True):
            if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.success(f"✅ ¡Bienvenido, {usuario}! Redirigiendo al panel...")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos. Inténtalo de nuevo.")

# ----------------- Logout -----------------
def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.df_cargado = None
    st.rerun()

# ----------------- Generar PDF (MEJORADA) -----------------
def generar_pdf(df_to_export):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Datos Hidrometeorológicos", ln=True, align="C")
    pdf.ln(10)

    # --- Sección de Resumen General ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="1. Resumen General del Conjunto de Datos", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, txt=f"  - Número total de filas: {len(df_to_export)}", ln=True)
    pdf.cell(0, 7, txt=f"  - Número total de columnas: {len(df_to_export.columns)}", ln=True)
    
    if isinstance(df_to_export.index, pd.DatetimeIndex):
        pdf.cell(0, 7, txt=f"  - Período de datos: {df_to_export.index.min().strftime('%Y-%m-%d')} a {df_to_export.index.max().strftime('%Y-%m-%d')}", ln=True)
    
    pdf.ln(5)

    # --- Sección de Resumen por Columna (Tipos de Datos y Valores Únicos) ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="2. Detalles de las Columnas", ln=True)
    pdf.set_font("Arial", '', 9) # Fuente más pequeña para detalles
    for col in df_to_export.columns:
        pdf.cell(0, 6, txt=f"  - '{col}':", ln=True)
        pdf.cell(0, 6, txt=f"    - Tipo de dato: {df_to_export[col].dtype}", ln=True)
        if df_to_export[col].dtype == 'object' or df_to_export[col].nunique() < 20: # Para columnas categóricas o con pocos valores únicos
            pdf.cell(0, 6, txt=f"    - Valores únicos: {df_to_export[col].nunique()}", ln=True)
        
        # Si es numérica, añadir estadísticas descriptivas
        if pd.api.types.is_numeric_dtype(df_to_export[col]):
            desc_stats = df_to_export[col].describe()
            pdf.cell(0, 6, txt=f"    - Media: {desc_stats['mean']:.2f}", ln=True)
            pdf.cell(0, 6, txt=f"    - Desviación Estándar: {desc_stats['std']:.2f}", ln=True)
            pdf.cell(0, 6, txt=f"    - Mínimo: {desc_stats['min']:.2f}", ln=True)
            pdf.cell(0, 6, txt=f"    - Máximo: {desc_stats['max']:.2f}", ln=True)
        pdf.ln(2) # Pequeño espacio entre columnas

    pdf.ln(5) # Espacio antes de la tabla

    # --- Sección de Datos Detallados (Tabla) ---
    pdf.add_page() # Nueva página para la tabla si es muy grande
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="3. Datos Detallados del Conjunto", ln=True, align="C")
    pdf.ln(5)

    df_str = df_to_export.astype(str)

    # Calcular ancho de columnas dinámicamente para la tabla
    num_cols_pdf = len(df_str.columns)
    has_index_name = df_str.index.name is not None and df_str.index.name != '' # Check if index has a meaningful name
    if has_index_name or isinstance(df_to_export.index, pd.DatetimeIndex): # Always show date index
        num_cols_pdf += 1 
        
    # Ancho aproximado de la página para la tabla, ajustado para evitar desbordamientos
    page_width = pdf.w - 2*pdf.l_margin
    col_width = page_width / num_cols_pdf
    
    # Si las columnas son muchas, ajustar el tamaño de fuente o dividir
    if num_cols_pdf > 6:
        pdf.set_font("Arial", 'B', 7) # Fuente más pequeña para encabezados
    else:
        pdf.set_font("Arial", 'B', 9)

    # Encabezados de la tabla
    if has_index_name:
        pdf.cell(col_width, 10, str(df_to_export.index.name), border=1, align='C')
    elif isinstance(df_to_export.index, pd.DatetimeIndex):
        pdf.cell(col_width, 10, "Fecha/Hora", border=1, align='C') # Generic name for datetime index
    
    for col in df_str.columns:
        pdf.cell(col_width, 10, str(col), border=1, align='C')
    pdf.ln()

    # Filas de datos
    if num_cols_pdf > 6:
        pdf.set_font("Arial", '', 6) # Fuente más pequeña para datos
    else:
        pdf.set_font("Arial", '', 7)

    for index, row in df_str.iterrows():
        # Valor del índice
        if has_index_name:
            if isinstance(index, pd.Timestamp):
                pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d %H:%M')), border=1)
            else:
                pdf.cell(col_width, 10, str(index), border=1)
        elif isinstance(df_to_export.index, pd.DatetimeIndex): # If index is datetime but no specific name
            pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d %H:%M')), border=1)
        
        # Valores de las columnas
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    buffer = BytesIO()
    pdf.output(buffer, 'S')
    pdf_data = buffer.getvalue()
    return pdf_data

# ----------------- Generar Word (MEJORADA) -----------------
def generar_word(df_to_export):
    doc = Document()
    
    # Título del Reporte
    doc.add_heading("Reporte de Datos Hidrometeorológicos", 0)
    doc.add_paragraph(f"Generado el: {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')}")
    doc.add_page_break()

    # --- Sección 1: Resumen General del Conjunto de Datos ---
    doc.add_heading("1. Resumen General del Conjunto de Datos", level=1)
    doc.add_paragraph(f"Número total de filas: {len(df_to_export)}")
    doc.add_paragraph(f"Número total de columnas: {len(df_to_export.columns)}")
    
    if isinstance(df_to_export.index, pd.DatetimeIndex):
        doc.add_paragraph(f"Período de datos: {df_to_export.index.min().strftime('%Y-%m-%d')} a {df_to_export.index.max().strftime('%Y-%m-%d')}")
    
    doc.add_paragraph("") # Espacio

    # --- Sección 2: Detalles de las Columnas ---
    doc.add_heading("2. Detalles de las Columnas", level=1)
    for col in df_to_export.columns:
        doc.add_paragraph(f"• **'{col}'**") # Usamos negritas para el nombre de la columna
        doc.add_paragraph(f"  - Tipo de dato: {df_to_export[col].dtype}")
        if df_to_export[col].dtype == 'object' or df_to_export[col].nunique() < 20:
            doc.add_paragraph(f"  - Valores únicos: {df_to_export[col].nunique()}")
        
        if pd.api.types.is_numeric_dtype(df_to_export[col]):
            desc_stats = df_to_export[col].describe()
            doc.add_paragraph(f"  - Media: {desc_stats['mean']:.2f}")
            doc.add_paragraph(f"  - Desviación Estándar: {desc_stats['std']:.2f}")
            doc.add_paragraph(f"  - Mínimo: {desc_stats['min']:.2f}")
            doc.add_paragraph(f"  - Máximo: {desc_stats['max']:.2f}")
        doc.add_paragraph("") # Espacio

    doc.add_page_break()

    # --- Sección 3: Datos Detallados del Conjunto (Tabla) ---
    doc.add_heading("3. Datos Detallados del Conjunto", level=1)
    
    # Calcular el número de columnas para la tabla de Word
    num_cols_word_table = len(df_to_export.columns)
    has_index_name = df_to_export.index.name is not None and df_to_export.index.name != ''
    if has_index_name or isinstance(df_to_export.index, pd.DatetimeIndex):
        num_cols_word_table += 1

    table = doc.add_table(rows=1, cols=num_cols_word_table)
    table.style = 'Table Grid' # Estilo de tabla con bordes

    # Encabezados de la tabla
    hdr_cells = table.rows[0].cells
    idx = 0
    if has_index_name:
        hdr_cells[idx].text = df_to_export.index.name
        idx += 1
    elif isinstance(df_to_export.index, pd.DatetimeIndex):
        hdr_cells[idx].text = "Fecha/Hora"
        idx += 1

    for i, col in enumerate(df_to_export.columns):
        hdr_cells[idx + i].text = col
        
    # Añadir filas de datos
    for index, row in df_to_export.iterrows():
        row_cells = table.add_row().cells
        idx = 0
        if has_index_name:
            if isinstance(index, pd.Timestamp):
                row_cells[idx].text = str(index.strftime('%Y-%m-%d %H:%M'))
            else:
                row_cells[idx].text = str(index)
            idx += 1
        elif isinstance(df_to_export.index, pd.DatetimeIndex):
            row_cells[idx].text = str(index.strftime('%Y-%m-%d %H:%M'))
            idx += 1

        for i, col_name in enumerate(df_to_export.columns):
            row_cells[idx + i].text = str(row[col_name])
            
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ----------------- Panel de Administración -----------------
def admin_panel():
    st.sidebar.title(f"👋 Hola, {st.session_state.usuario}!")
    st.sidebar.button("Cerrar Sesión", on_click=logout, type="secondary", use_container_width=True)
    st.sidebar.markdown("---")

    st.title("💡 Dashboard Hidrometeorológico Interactivo")
    st.markdown("Una plataforma moderna para el análisis y visualización de datos climáticos.")
    st.markdown("---")

    tab_carga, tab_analisis, tab_exportacion = st.tabs(["📂 Cargar Datos", "📊 Análisis y Visualización", "📤 Exportar Reportes"])

    with tab_carga:
        st.header("Sube tus Datos CSV")
        st.info("Aquí puedes cargar tus archivos de datos hidrometeorológicos en formato CSV.")
        
        uploaded_file = st.file_uploader("Arrastra y suelta tu archivo CSV aquí o haz clic para buscarlo", type=["csv"],
                                         help="Asegúrate de que tu archivo CSV esté bien formateado.")

        if uploaded_file is None:
            st.session_state.df_cargado = None
            st.warning("Aún no hay datos cargados. Por favor, sube un archivo CSV para empezar a analizar.")
        else:
            with st.spinner("Cargando y procesando datos..."):
                try: 
                    df = pd.read_csv(uploaded_file)
                    st.success("¡CSV cargado exitosamente! 🎉")

                    fecha_col_candidatas = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
                    
                    df_copy = df.copy()

                    if fecha_col_candidatas:
                        for col_name in fecha_col_candidatas:
                            try:
                                df_copy[col_name] = pd.to_datetime(df_copy[col_name], errors='coerce')
                                if not df_copy[col_name].isna().all():
                                    df_copy.set_index(col_name, inplace=True)
                                    st.info(f"Columna '{col_name}' detectada y establecida como índice de tiempo. ✅")
                                    break
                            except Exception: 
                                pass
                    
                    if not isinstance(df_copy.index, pd.DatetimeIndex):
                         st.info("No se encontró una columna de fecha/hora automática.")
                         if st.checkbox("¿Tu archivo tiene una columna de fecha/hora para el índice?"):
                            date_column_options = [col for col in df.columns if df[col].dtype == 'object']
                            if date_column_options:
                                date_column = st.selectbox("Selecciona la columna de fecha/hora:", options=date_column_options)
                                if date_column:
                                    try:
                                        df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
                                        if not df_copy[date_column].isna().all():
                                            df_copy.set_index(date_column, inplace=True)
                                            st.success(f"Columna '{date_column}' establecida como índice de tiempo. ✅")
                                        else:
                                            st.warning(f"La columna '{date_column}' no pudo convertirse a fecha/hora. Asegúrate del formato.")
                                    except Exception as e: 
                                        st.error(f"Error al convertir la columna '{date_column}' a formato de fecha/hora: {e}")
                            else:
                                st.warning("No hay columnas de texto que puedan ser fechas. Asegúrate del formato.")

                    st.subheader("📋 Vista Previa de los Datos Cargados")
                    st.dataframe(df_copy)
                    st.session_state.df_cargado = df_copy

                except Exception as e: 
                    st.error(f"¡Oops! Parece que hubo un error al leer tu archivo CSV: {e} 💔")
                    st.info("Por favor, verifica que el archivo es un CSV válido y no está corrupto. Intenta con otro archivo.")
                    st.session_state.df_cargado = None

    df_actual = st.session_state.df_cargado

    with tab_analisis:
        st.header("Exploración y Visualización de Datos")
        st.info("Usa estas herramientas para interactuar con tus datos cargados y generar visualizaciones dinámicas.")

        if df_actual is not None and not df_actual.empty:
            
            st.subheader("🎨 Configura tu Gráfico Interactivo")
            col_graph_type, col_x_axis, col_y_axis = st.columns(3)

            with col_graph_type:
                graph_type = st.selectbox(
                    "Selecciona el Tipo de Gráfico:",
                    options=["Líneas", "Dispersión", "Barras", "Histograma", "Caja", "Correlación"],
                    help="Elige la representación visual que mejor se adapte a tu análisis."
                )
            
            numeric_cols = df_actual.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df_actual.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if isinstance(df_actual.index, pd.DatetimeIndex):
                index_name = df_actual.index.name if df_actual.index.name else 'Fecha/Índice'
                numeric_cols.insert(0, index_name)
            
            if graph_type == "Correlación":
                with col_x_axis:
                    st.empty()
                with col_y_axis:
                    st.empty()
                if not numeric_cols:
                    st.warning("No hay columnas numéricas para generar la matriz de correlación.")
                elif len(numeric_cols) < 2:
                     st.info("Necesitas al menos dos columnas numéricas para ver la correlación.")
                else:
                    st.subheader("📊 Matriz de Correlación")
                    try:
                        cols_for_corr = [col for col in numeric_cols if col != index_name and pd.api.types.is_numeric_dtype(df_actual[col])]
                        if cols_for_corr:
                            fig_corr = px.imshow(df_actual[cols_for_corr].corr(), text_auto=True, color_continuous_scale=px.colors.sequential.Viridis,
                                                title="Relación entre Variables Numéricas")
                            st.plotly_chart(fig_corr, use_container_width=True)
                        else:
                            st.info("No hay columnas numéricas adecuadas para calcular la correlación.")

                    except Exception as e:
                        st.error(f"Error al generar el gráfico de correlación: {e}")

            elif graph_type in ["Líneas", "Dispersión", "Barras", "Histograma", "Caja"]:
                with col_x_axis:
                    x_axis_options = df_actual.columns.tolist()
                    if isinstance(df_actual.index, pd.DatetimeIndex) and df_actual.index.name:
                        x_axis_options.insert(0, df_actual.index.name)
                    elif isinstance(df_actual.index, pd.DatetimeIndex):
                        x_axis_options.insert(0, 'index')

                    x_axis = st.selectbox("Eje X:", options=x_axis_options, key="x_axis_select")
                with col_y_axis:
                    y_axis_options = [col for col in df_actual.columns.tolist() if col != x_axis and pd.api.types.is_numeric_dtype(df_actual[col])]
                    y_axis = st.selectbox("Eje Y:", options=y_axis_options, key="y_axis_select")

                if x_axis and y_axis:
                    try:
                        plot_df = df_actual.copy()
                        if isinstance(df_actual.index, pd.DatetimeIndex) and x_axis == df_actual.index.name:
                            plot_df = plot_df.reset_index()
                        elif isinstance(df_actual.index, pd.DatetimeIndex) and x_axis == 'index':
                             plot_df = plot_df.reset_index(names=['index'])
                        
                        if graph_type == "Líneas":
                            fig = px.line(plot_df, x=x_axis, y=y_axis, title=f"Tendencia de {y_axis} vs {x_axis}")
                        elif graph_type == "Dispersión":
                            fig = px.scatter(plot_df, x=x_axis, y=y_axis, title=f"Dispersión de {y_axis} vs {x_axis}")
                        elif graph_type == "Barras":
                            fig = px.bar(plot_df, x=x_axis, y=y_axis, title=f"Barras de {y_axis} por {x_axis}")
                        elif graph_type == "Histograma":
                            fig = px.histogram(plot_df, x=x_axis, title=f"Distribución de {x_axis}", marginal="rug")
                        elif graph_type == "Caja":
                            fig = px.box(plot_df, x=x_axis, y=y_axis, title=f"Distribución en Caja de {y_axis} por {x_axis}")
                        
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"No se pudo generar el gráfico de {graph_type}. Asegúrate de seleccionar columnas apropiadas. Error: {e}")
                else:
                    st.info("Selecciona las columnas para el eje X y Y para generar el gráfico.")
            else:
                st.info("Selecciona un tipo de gráfico para comenzar la visualización.")

        else:
            st.info("Carga un archivo CSV en la pestaña 'Cargar Datos' para visualizar aquí.")

    with tab_exportacion:
        st.header("Generar y Exportar Reportes")
        st.info("Aquí puedes generar y descargar tus reportes
