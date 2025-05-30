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

    # Calcular el número total de columnas incluyendo el índice si es relevante
    num_cols_display = len(df_to_export.columns)
    include_index_col = False
    if df_to_export.index.name or not isinstance(df_to_export.index, pd.RangeIndex):
        include_index_col = True
        num_cols_display += 1

    col_width = pdf.w / num_cols_display 
    
    # Añadir los encabezados de las columnas
    if include_index_col:
        pdf.cell(col_width, 10, str(df_to_export.index.name if df_to_export.index.name else "Índice"), border=1)
    for col in df_to_export.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()

    # Añadir los datos
    for index, row in df_to_export.iterrows():
        if include_index_col:
            # Manejar el índice, especialmente si es un Timestamp
            if isinstance(index, pd.Timestamp):
                pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d')), border=1)
            else:
                pdf.cell(col_width, 10, str(index), border=1)
        
        # Añadir los valores de las filas
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    buffer = BytesIO()
    pdf_data = pdf.output(dest='S').encode('latin-1') 
    buffer.write(pdf_data)
    buffer.seek(0)
    
    return buffer.getvalue()

# ----------------- Generar Word -----------------
def generar_word(df_to_export):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    
    columns_for_word = []
    include_index_col = False
    if df_to_export.index.name or not isinstance(df_to_export.index, pd.RangeIndex):
        include_index_col = True
        columns_for_word.append(df_to_export.index.name if df_to_export.index.name else "Índice")
    
    columns_for_word.extend(df_to_export.columns.tolist())

    table = doc.add_table(rows=1, cols=len(columns_for_word))
    hdr_cells = table.rows[0].cells
    for i, col_name in enumerate(columns_for_word):
        hdr_cells[i].text = col_name
    
    for index, row in df_to_export.iterrows():
        row_cells = table.add_row().cells
        cell_idx = 0

        if include_index_col:
            if isinstance(index, pd.Timestamp):
                row_cells[cell_idx].text = str(index.strftime('%Y-%m-%d'))
            else:
                row_cells[cell_idx].text = str(index)
            cell_idx += 1

        for col_name in df_to_export.columns:
            row_cells[cell_idx].text = str(row[col_name])
            cell_idx += 1
            
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# ----------------- Panel de Administración -----------------
def admin_panel():
    st.title("🛠️ Panel de Administración")
    st.write(f"Bienvenido, {st.session_state.usuario}")

    st.subheader("📁 Cargar Datos (CSV)")
    uploaded_file = st.file_uploader("Sube tu archivo CSV para visualizar los datos", type=["csv"])

    # Aquí inicializamos df_actual a None si no hay archivo cargado
    df_actual = st.session_state.df_cargado if 'df_cargado' in st.session_state else None


    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo CSV cargado exitosamente.")

            # --- Procesamiento de Fecha ---
            if 'fecha' in df.columns and pd.api.types.is_string_dtype(df['fecha']):
                try:
                    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                    df.dropna(subset=['fecha'], inplace=True)
                    df.set_index('fecha', inplace=True)
                    st.info("Columna 'fecha' detectada y establecida como índice de tiempo.")
                except Exception as e:
                    st.warning(f"No se pudo convertir la columna 'fecha' a formato de fecha/hora. Error: {e}")
            elif st.checkbox("¿Tu archivo tiene una columna de fecha/hora para el índice?"):
                date_column = st.selectbox("Selecciona la columna de fecha/hora:", df.columns)
                if date_column:
                    try:
                        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
                        df.dropna(subset=[date_column], inplace=True)
                        df.set_index(date_column, inplace=True)
                        st.info(f"Columna '{date_column}' detectada y establecida como índice de tiempo.")
                    except Exception as e:
                        st.error(f"Error al convertir la columna '{date_column}' a formato de fecha/hora: {e}")
            
            st.subheader("Vista Previa de los Datos")
            st.dataframe(df)

            st.session_state.df_cargado = df
            df_actual = df # Actualizar df_actual con el nuevo DataFrame cargado

        except Exception as e:
            st.error(f"Error al leer el archivo CSV: {e}")
            st.info("Asegúrate de que el archivo es un CSV válido y no está dañado.")
            st.session_state.df_cargado = None
            df_actual = None # Asegurar que df_actual sea None en caso de error de carga
    
    if df_actual is None or df_actual.empty:
        st.info("Sube un archivo CSV para empezar a visualizar y analizar tus datos.")
    else:
        # --- Controles Globales del Dashboard ---
        st.sidebar.header("⚙️ Opciones del Dashboard")
        
        # Filtro de fecha si el índice es de tipo datetime
        df_filtrado = df_actual # Inicializar df_filtrado con el DataFrame completo
        if isinstance(df_actual.index, pd.DatetimeIndex):
            min_date_available = df_actual.index.min().date()
            max_date_available = df_actual.index.max().date()
            
            date_range = st.sidebar.date_input(
                "Selecciona un rango de fechas:",
                value=(min_date_available, max_date_available),
                min_value=min_date_available,
                max_value=max_date_available
            )
            
            if len(date_range) == 2:
                start_date = min(date_range)
                end_date = max(date_range)
                # Asegurar que las fechas son de tipo Timestamp para la indexación
                df_filtrado = df_actual.loc[pd.to_datetime(start_date):pd.to_datetime(end_date)]
                st.sidebar.info(f"Datos filtrados del {start_date} al {end_date}.")
            else:
                st.sidebar.info("Selecciona un rango de fechas completo (inicio y fin).")

        # --- Sección de Visualización Dinámica ---
        st.subheader("📊 Visualización Dinámica de Datos")

        # Obtener columnas numéricas y categóricas del DataFrame filtrado
        numeric_df = df_filtrado.select_dtypes(include=['number']) # Usar df_filtrado para los gráficos
        columnas_numericas = numeric_df.columns.tolist()
        columnas_categoricas = df_filtrado.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        
        # Añadir el índice como una opción si es de tipo numérico o si queremos usarlo para plotear
        if isinstance(df_filtrado.index, (pd.Int64Index, pd.Float64Index)):
            columnas_numericas.insert(0, df_filtrado.index.name if df_filtrado.index.name else "Índice Numérico")

        if not df_filtrado.empty:
            
            # Selector de tipo de gráfico
            chart_type = st.selectbox(
                "Selecciona el tipo de gráfico:",
                options=["Gráfico de Línea (Serie de Tiempo)", "Histograma", "Gráfico de Dispersión (Scatter)", 
                         "Gráfico de Barras", "Box Plot", "Violin Plot", "Gráfico de Correlación (Heatmap)"],
                key="chart_selector"
            )

            # --- Generación de Gráficos Basado en Selección ---
            if chart_type == "Gráfico de Línea (Serie de Tiempo)":
                if isinstance(df_filtrado.index, pd.DatetimeIndex) and not df_filtrado.empty:
                    st.line_chart(df_filtrado)
                else:
                    st.warning("Este gráfico requiere un índice de fecha/hora y datos no vacíos.")
                    if not df_filtrado.empty: st.dataframe(df_filtrado) # Mostrar datos si no hay índice de fecha
            
            elif chart_type == "Histograma":
                if columnas_numericas and not df_filtrado.empty:
                    hist_column = st.selectbox("Selecciona columna para Histograma:", options=columnas_numericas, key="hist_col_dyn")
                    if hist_column:
                        fig_hist = px.histogram(df_filtrado, x=hist_column, marginal="rug", title=f"Distribución de {hist_column}")
                        st.plotly_chart(fig_hist)
                else:
                    st.info("No hay columnas numéricas o datos para generar histogramas.")

            elif chart_type == "Gráfico de Dispersión (Scatter)":
                if len(columnas_numericas) >= 2 and not df_filtrado.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        x_axis = st.selectbox("Eje X:", options=columnas_numericas, key="scatter_x_dyn")
                    with col2:
                        y_axis = st.selectbox("Eje Y:", options=columnas_numericas, key="scatter_y_dyn")
                    
                    color_by = st.selectbox("Color por (opcional):", options=["Ninguno"] + columnas_categoricas + columnas_numericas, key="scatter_color_dyn")
                    size_by = st.selectbox("Tamaño por (opcional):", options=["Ninguno"] + columnas_numericas, key="scatter_size_dyn")
                    
                    if x_axis and y_axis:
                        color_col = color_by if color_by != "Ninguno" else None
                        size_col = size_by if size_by != "Ninguno" else None
                        
                        fig_scatter = px.scatter(
                            df_filtrado, 
                            x=x_axis, 
                            y=y_axis, 
                            color=color_col, 
                            size=size_col, 
                            title=f"Dispersión de {x_axis} vs {y_axis}"
                        )
                        st.plotly_chart(fig_scatter)
                else:
                    st.info("Necesitas al menos dos columnas numéricas y datos para este gráfico.")
            
            elif chart_type == "Gráfico de Barras":
                # La lista de opciones para bar_x_dyn debe incluir las columnas categóricas,
                # y si el índice es apropiado (no DatetimeIndex)
                bar_x_options = columnas_categoricas[:]
                if df_filtrado.index.name and not isinstance(df_filtrado.index, pd.DatetimeIndex):
                    bar_x_options.insert(0, df_filtrado.index.name)
                elif not isinstance(df_filtrado.index, pd.RangeIndex) and not isinstance(df_filtrado.index, pd.DatetimeIndex):
                     bar_x_options.insert(0, "Índice") # Si es un índice significativo sin nombre y no fecha

                if columnas_numericas and bar_x_options and not df_filtrado.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        bar_x = st.selectbox("Eje X (Categoría/Etiqueta):", options=bar_x_options, key="bar_x_dyn")
                    with col2:
                        bar_y = st.selectbox("Eje Y (Valor Numérico):", options=columnas_numericas, key="bar_y_dyn")
                    
                    if bar_x and bar_y:
                        # Asegurarse de que el eje X se toma correctamente si es el índice
                        x_data = df_filtrado.index if bar_x in ["Índice", df_filtrado.index.name] else df_filtrado[bar_x]
                        fig_bar = px.bar(df_filtrado, x=x_data, y=bar_y, title=f"Gráfico de Barras de {bar_y} por {bar_x}")
                        st.plotly_chart(fig_bar)
                else:
                    st.info("Necesitas columnas numéricas y categóricas (o un índice apropiado) y datos para este gráfico.")

            elif chart_type == "Box Plot":
                if columnas_numericas and not df_filtrado.empty:
                    box_y = st.selectbox("Variable a analizar (Eje Y):", options=columnas_numericas, key="box_y_dyn")
                    box_x_cat = st.selectbox("Categoría para agrupar (Eje X, opcional):", options=["Ninguno"] + columnas_categoricas, key="box_x_dyn")
                    
                    if box_y:
                        fig_box = px.box(df_filtrado, y=box_y, x=box_x_cat if box_x_cat != "Ninguno" else None, title=f"Box Plot de {box_y}")
                        st.plotly_chart(fig_box)
                else:
                    st.info("No hay columnas numéricas o datos para generar Box Plots.")

            elif chart_type == "Violin Plot":
                if columnas_numericas and not df_filtrado.empty:
                    violin_y = st.selectbox("Variable a analizar (Eje Y):", options=columnas_numericas, key="violin_y_dyn")
                    violin_x_cat = st.selectbox("Categoría para agrupar (Eje X, opcional):", options=["Ninguno"] + columnas_categoricas, key="violin_x_dyn")
                    
                    if violin_y:
                        fig_violin = px.violin(df_filtrado, y=violin_y, x=violin_x_cat if violin_x_cat != "Ninguno" else None, title=f"Violin Plot de {violin_y}")
                        st.plotly_chart(fig_violin)
                else:
                    st.info("No hay columnas numéricas o datos para generar Violin Plots.")

            elif chart_type == "Gráfico de Correlación (Heatmap)":
                if not numeric_df.empty and not df_filtrado.empty:
                    try:
                        # Aquí, el heatmap de correlación se hace sobre el numeric_df original (no filtrado por fecha)
                        # o sobre el filtrado, dependiendo de si quieres correlación de todo o solo del rango seleccionado
                        # Lo dejé con el df_filtrado para que sea consistente con el resto
                        fig = px.imshow(numeric_df.corr(), text_auto=True, title="Matriz de Correlación")
                        st.plotly_chart(fig)
                    except Exception as e:
                        st.warning(f"No se pudo generar el gráfico de correlación. Asegúrate de tener al menos dos columnas numéricas y datos. Error: {e}")
                else:
                    st.warning("El DataFrame no contiene columnas numéricas o datos para generar un gráfico de correlación.")

        else:
            st.warning("El DataFrame actual está vacío o no tiene datos después del filtrado. Ajusta el rango de fechas o carga un archivo.")

        # --- Sección de Exportación ---
        st.subheader("📤 Exportar Datos")
        
        # Generar los datos para la descarga solo si df_filtrado no está vacío
        if not df_filtrado.empty:
            pdf_data = generar_pdf(df_filtrado)
            word_data = generar_word(df_filtrado)

            st.download_button(
                label="📄 Descargar PDF de datos filtrados",
                data=pdf_data,
                file_name="reporte_filtrado.pdf",
                mime="application/pdf"
            )

            st.download_button(
                label="📝 Descargar Word de datos filtrados",
                data=word_data,
                file_name="reporte_filtrado.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.info("No hay datos para exportar. Carga un archivo o ajusta los filtros.")

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
    
