import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
from docx import Document

# ----------------- Configuración del Tema (Colores Claros) -----------------
st.set_page_config(
    page_title="💧Hydromet | Centro de control de datos ambientales",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Puedes personalizar estos colores para un estilo más específico
primary_color = "#4CAF50"  # Verde esmeralda claro
background_color = "#F0F2F6"  # Gris muy claro
secondary_background_color = "#FFFFFF"  # Blanco puro
text_color = "#31333F"  # Gris oscuro

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {background_color};
        color: {text_color};
    }}
    .css-1d391kg {{ /* Sidebar background */
        background-color: {secondary_background_color};
    }}
    .css-1lcbmhc {{ /* Main content background */
        background-color: {background_color};
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #45a049; /* Un poco más oscuro al pasar el ratón */
    }}
    .stTextInput>div>div>input {{
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
    }}
    .stSelectbox>div>div>div {{
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 5px;
    }}
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
        color: {primary_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- Autenticación -----------------
USUARIOS = {
    "admin": "YZ1BKzgHIK7P7ZrB",
    "tecnico": "tecnico123"
}

# ----------------- Login -----------------
def login():
    st.title("💧Hydromet | Centro de control de datos ambientales")
    st.markdown("---") # Línea horizontal para separar el título

    st.subheader("Accede a tu cuenta")
    usuario = st.text_input("Usuario", key="login_user")
    contraseña = st.text_input("Contraseña", type="password", key="login_password")
    
    col1, col2 = st.columns([1, 6])
    with col1:
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
    pdf.cell(200, 10, txt="Reporte de Datos - 💧Hydromet", ln=True, align="C")
    pdf.ln()
    
    # Añadir el dataframe como tabla en el PDF
    if not df.empty:
        # Calcular ancho de columnas dinámicamente o establecer un ancho fijo
        col_width = pdf.w / (len(df.columns) + 1)
        
        # Encabezados de la tabla
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), border=1, align='C')
        pdf.ln()

        # Filas de la tabla
        for index, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 10, str(item), border=1)
            pdf.ln()

    return pdf.output(dest='S').encode('latin-1')


# ----------------- Exportar a Word -----------------
def generar_word(df):
    doc = Document()
    doc.add_heading("Reporte de Datos - 💧Hydromet", 0)
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
    uploaded_file = st.file_uploader("📁 Cargar archivo CSV", type=["csv"], help="Sube tu archivo CSV para analizar los datos.")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])
                df.set_index('fecha', inplace=True)
                st.success("CSV cargado y columna 'fecha' establecida como índice. ¡Listo para el análisis! 🎉")
            else:
                st.warning("La columna 'fecha' no se encontró. Se cargarán los datos sin establecer un índice de tiempo.")
            st.session_state.df_cargado = df
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e} 😞 Asegúrate de que es un CSV válido.")
            st.session_state.df_cargado = None

# ----------------- Panel del Administrador -----------------
def admin_panel():
    st.sidebar.title("Menú 📊")
    st.sidebar.markdown(f"Bienvenido, **{st.session_state.usuario}** 👋")

    st.sidebar.markdown("---")
    st.sidebar.header("Opciones de Datos")
    cargar_datos()

    df = st.session_state.get('df_cargado')

    if df is not None:
        st.sidebar.markdown("---")
        st.sidebar.header("Navegación de Gráficos")
        chart_options = [
            "Vista Previa de Datos 📄",
            "Estadísticas Descriptivas 📊",
            "Serie de Tiempo 📈",
            "Correlación 🔗",
            "Dispersión 📌",
            "Histograma 📈",
            "Gráfico de Barras 📊",
            "Gráfico de Tarta 🥧",
            "Gráfico de Caja (Box Plot) 📦",
            "Gráfico de Violín 🎻",
            "Gráfico de Densidad 📈",
            "Gráfico de Área ⛰️",
            "Exportar Datos 📤"
        ]
        selected_chart = st.sidebar.radio("Selecciona una herramienta:", chart_options)
        
        st.title("🛠️ Panel de Administración - 💧Hydromet")
        st.markdown("---") # Separador para el título principal

        if selected_chart == "Vista Previa de Datos 📄":
            st.subheader("📄 Vista Previa de los Datos Cargados")
            st.write(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
            st.dataframe(df.head(10)) # Mostrar solo las primeras 10 filas por defecto
            if st.checkbox("Mostrar DataFrame Completo"):
                st.dataframe(df)

        elif selected_chart == "Estadísticas Descriptivas 📊":
            st.subheader("📊 Estadísticas Descriptivas")
            st.write(df.describe())

        elif selected_chart == "Serie de Tiempo 📈":
            st.subheader("📈 Visualización de Serie de Tiempo")
            if 'fecha' in df.index.name:
                numeric_cols = df.select_dtypes(include='number').columns.tolist()
                if numeric_cols:
                    selected_time_series_col = st.selectbox("Selecciona una columna para la serie de tiempo:", numeric_cols)
                    if selected_time_series_col:
                        fig_time_series = px.line(df, y=selected_time_series_col, title=f"Serie de Tiempo de {selected_time_series_col}")
                        st.plotly_chart(fig_time_series)
                else:
                    st.warning("No hay columnas numéricas para graficar la serie de tiempo.")
            else:
                st.warning("La columna 'fecha' no está establecida como índice para la visualización de serie de tiempo.")

        elif selected_chart == "Correlación 🔗":
            st.subheader("🔗 Matriz de Correlación")
            numeric_df = df.select_dtypes(include='number')
            if not numeric_df.empty:
                fig = px.imshow(numeric_df.corr(), text_auto=True, color_continuous_scale=px.colors.sequential.Viridis, title="Matriz de Correlación")
                st.plotly_chart(fig)
            else:
                st.info("No hay datos numéricos para calcular la correlación.")

        elif selected_chart == "Dispersión 📌":
            st.subheader("📌 Gráfico de Dispersión")
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("Eje X", numeric_cols, key="scatter_x")
                y_col = st.selectbox("Eje Y", numeric_cols, key="scatter_y")
                color_col_options = ['Ninguno'] + df.columns.tolist()
                color_col = st.selectbox("Color por", color_col_options, key="scatter_color")

                if x_col and y_col:
                    if color_col != 'Ninguno':
                        fig_scatter = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"Dispersión de {x_col} vs {y_col} por {color_col}")
                    else:
                        fig_scatter = px.scatter(df, x=x_col, y=y_col, title=f"Dispersión de {x_col} vs {y_col}")
                    st.plotly_chart(fig_scatter)
            else:
                st.info("Necesitas al menos dos columnas numéricas para un gráfico de dispersión.")

        elif selected_chart == "Histograma 📈":
            st.subheader("📈 Histograma de Distribución")
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                col_hist = st.selectbox("Selecciona la columna para el histograma:", numeric_cols, key="hist_col")
                bins = st.slider("Número de Bins", 5, 50, 20)
                fig_hist = px.histogram(df, x=col_hist, nbins=bins, marginal="rug", title=f"Histograma de {col_hist}")
                st.plotly_chart(fig_hist)
            else:
                st.info("No hay columnas numéricas para generar histogramas.")

        # --- Nuevas Herramientas Gráficas (Exclusivas para el Administrador) ---
        elif selected_chart == "Gráfico de Barras 📊":
            st.subheader("📊 Gráfico de Barras Interactivo")
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            numeric_cols = df.select_dtypes(include='number').columns.tolist()

            if categorical_cols and numeric_cols:
                x_bar = st.selectbox("Eje X (Categoría)", categorical_cols, key="bar_x")
                y_bar = st.selectbox("Eje Y (Valor Numérico)", numeric_cols, key="bar_y")
                
                if x_bar and y_bar:
                    agg_func = st.selectbox("Función de Agregación", ["sum", "mean", "count", "median"], key="bar_agg")
                    
                    if agg_func == "sum":
                        df_agg = df.groupby(x_bar)[y_bar].sum().reset_index()
                    elif agg_func == "mean":
                        df_agg = df.groupby(x_bar)[y_bar].mean().reset_index()
                    elif agg_func == "count":
                        df_agg = df.groupby(x_bar)[y_bar].count().reset_index()
                    elif agg_func == "median":
                        df_agg = df.groupby(x_bar)[y_bar].median().reset_index()
                    
                    fig_bar = px.bar(df_agg, x=x_bar, y=y_bar, title=f"Gráfico de Barras de {y_bar} por {x_bar} ({agg_func})")
                    st.plotly_chart(fig_bar)
            else:
                st.info("Necesitas columnas categóricas y numéricas para generar un gráfico de barras.")

        elif selected_chart == "Gráfico de Tarta 🥧":
            st.subheader("🥧 Gráfico de Tarta (Distribución Categórica)")
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if categorical_cols:
                names_pie = st.selectbox("Columna para las Categorías (Nombres)", categorical_cols, key="pie_names")
                values_pie_options = ['Conteo'] + df.select_dtypes(include='number').columns.tolist()
                values_pie = st.selectbox("Columna para los Valores (Tamaño)", values_pie_options, key="pie_values")

                if names_pie:
                    if values_pie == 'Conteo':
                        fig_pie = px.pie(df, names=names_pie, title=f"Distribución de {names_pie} (Conteo)")
                    else:
                        fig_pie = px.pie(df, names=names_pie, values=values_pie, title=f"Distribución de {names_pie} por {values_pie}")
                    st.plotly_chart(fig_pie)
            else:
                st.info("Necesitas al menos una columna categórica para generar un gráfico de tarta.")

        elif selected_chart == "Gráfico de Caja (Box Plot) 📦":
            st.subheader("📦 Gráfico de Caja (Box Plot)")
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

            if numeric_cols:
                y_box = st.selectbox("Eje Y (Columna Numérica)", numeric_cols, key="box_y")
                x_box_options = ['Ninguno'] + categorical_cols
                x_box = st.selectbox("Agrupar por (Columna Categórica)", x_box_options, key="box_x")

                if y_box:
                    if x_box != 'Ninguno':
                        fig_box = px.box(df, y=y_box, x=x_box, title=f"Box Plot de {y_box} agrupado por {x_box}")
                    else:
                        fig_box = px.box(df, y=y_box, title=f"Box Plot de {y_box}")
                    st.plotly_chart(fig_box)
            else:
                st.info("Necesitas columnas numéricas para generar un Box Plot.")

        elif selected_chart == "Gráfico de Violín 🎻":
            st.subheader("🎻 Gráfico de Violín")
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

            if numeric_cols:
                y_violin = st.selectbox("Eje Y (Columna Numérica)", numeric_cols, key="violin_y")
                x_violin_options = ['Ninguno'] + categorical_cols
                x_violin = st.selectbox("Agrupar por (Columna Categórica)", x_violin_options, key="violin_x")

                if y_violin:
                    if x_violin != 'Ninguno':
                        fig_violin = px.violin(df, y=y_violin, x=x_violin, box=True, points="all", title=f"Gráfico de Violín de {y_violin} agrupado por {x_violin}")
                    else:
                        fig_violin = px.violin(df, y=y_violin, box=True, points="all", title=f"Gráfico de Violín de {y_violin}")
                    st.plotly_chart(fig_violin)
            else:
                st.info("Necesitas columnas numéricas para generar un gráfico de violín.")

        elif selected_chart == "Gráfico de Densidad 📈":
            st.subheader("📈 Gráfico de Densidad (KDE Plot)")
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                x_density = st.selectbox("Selecciona la columna para la densidad:", numeric_cols, key="density_x")
                if x_density:
                    fig_density = px.density_contour(df, x=x_density, marginal="rug", title=f"Gráfico de Densidad para {x_density}")
                    st.plotly_chart(fig_density)
            else:
                st.info("No hay columnas numéricas para generar gráficos de densidad.")

        elif selected_chart == "Gráfico de Área ⛰️":
            st.subheader("⛰️ Gráfico de Área")
            if 'fecha' in df.index.name:
                numeric_cols = df.select_dtypes(include='number').columns.tolist()
                if numeric_cols:
                    y_area = st.selectbox("Columna Y para el Área", numeric_cols, key="area_y")
                    if y_area:
                        fig_area = px.area(df, y=y_area, title=f"Gráfico de Área para {y_area}")
                        st.plotly_chart(fig_area)
                else:
                    st.info("No hay columnas numéricas para generar gráficos de área.")
            else:
                st.warning("La columna 'fecha' no está establecida como índice para la visualización de gráficos de área.")

        elif selected_chart == "Exportar Datos 📤":
            st.subheader("📤 Exportar Datos")
            st.download_button("📄 Descargar PDF", data=generar_pdf(df), file_name="reporte_hydromet.pdf", mime="application/pdf")
            st.download_button("📝 Descargar Word", data=generar_word(df), file_name="reporte_hydromet.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.info("Por favor, carga un archivo CSV en la barra lateral para comenzar a analizar los datos. 👆")

    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión 🚪"):
        logout()

# ----------------- Panel del Técnico -----------------
def tecnico_panel():
    st.sidebar.title("Menú 🔧")
    st.sidebar.markdown(f"Bienvenido, **{st.session_state.usuario}** 👋")

    st.sidebar.markdown("---")
    st.sidebar.header("Opciones de Datos")
    cargar_datos()

    df = st.session_state.get('df_cargado')
    
    st.title("🔧 Panel Técnico - 💧Hydromet")
    st.markdown("---") # Separador para el título principal

    if df is not None:
        st.sidebar.markdown("---")
        st.sidebar.header("Navegación de Gráficos")
        chart_options = [
            "Vista Previa de Datos 📄",
            "Serie de Tiempo 📈",
            "Correlación 🔗",
            "Exportar Datos 📤"
        ]
        selected_chart = st.sidebar.radio("Selecciona una herramienta:", chart_options)

        if selected_chart == "Vista Previa de Datos 📄":
            st.subheader("📄 Vista Previa de los Datos Cargados")
            st.write(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
            st.dataframe(df.head(10))
            if st.checkbox("Mostrar DataFrame Completo"):
                st.dataframe(df)

        elif selected_chart == "Serie de Tiempo 📈":
            st.subheader("📈 Visualización de Serie de Tiempo")
            if 'fecha' in df.index.name:
                numeric_cols = df.select_dtypes(include='number').columns.tolist()
                if numeric_cols:
                    selected_time_series_col = st.selectbox("Selecciona una columna para la serie de tiempo:", numeric_cols)
                    if selected_time_series_col:
                        fig_time_series = px.line(df, y=selected_time_series_col, title=f"Serie de Tiempo de {selected_time_series_col}")
                        st.plotly_chart(fig_time_series)
                else:
                    st.warning("No hay columnas numéricas para graficar la serie de tiempo.")
            else:
                st.warning("La columna 'fecha' no está establecida como índice para la visualización de serie de tiempo.")

        elif selected_chart == "Correlación 🔗":
            st.subheader("🔗 Matriz de Correlación")
            numeric_df = df.select_dtypes(include='number')
            if not numeric_df.empty:
                fig = px.imshow(numeric_df.corr(), text_auto=True, color_continuous_scale=px.colors.sequential.Viridis, title="Matriz de Correlación")
                st.plotly_chart(fig)
            else:
                st.info("No hay datos numéricos para calcular la correlación.")

        elif selected_chart == "Exportar Datos 📤":
            st.subheader("📤 Exportar Datos")
            st.download_button("📄 Descargar PDF", data=generar_pdf(df), file_name="reporte_hydromet.pdf", mime="application/pdf")
            st.download_button("📝 Descargar Word", data=generar_word(df), file_name="reporte_hydromet.docx",
                               mime="application/vnd.openxmlformats-offi
