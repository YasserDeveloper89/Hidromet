# ... (Tu código existente: imports, USUARIOS, login, logout, generar_pdf, generar_word) ...

# ----------------- Panel de Administración -----------------
def admin_panel():
    st.title("🛠️ Panel de Administración")
    st.write(f"Bienvenido, {st.session_state.usuario}")

    st.subheader("📁 Cargar Datos (CSV)")
    uploaded_file = st.file_uploader("Sube tu archivo CSV para visualizar los datos", type=["csv"])

    if uploaded_file is None:
        st.session_state.df_cargado = None
        st.info("Sube un archivo CSV para empezar a visualizar y analizar tus datos.")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo CSV cargado exitosamente.")

            # --- Procesamiento de Fecha ---
            # Intentar detectar automáticamente la columna 'fecha' o permitir selección
            if 'fecha' in df.columns and pd.api.types.is_string_dtype(df['fecha']):
                try:
                    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                    # Eliminar filas donde la fecha no pudo ser parseada
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

        except Exception as e:
            st.error(f"Error al leer el archivo CSV: {e}")
            st.info("Asegúrate de que el archivo es un CSV válido y no está dañado.")
            st.session_state.df_cargado = None
    
    df_actual = st.session_state.df_cargado

    if df_actual is not None and not df_actual.empty:
        
        # --- Controles Globales del Dashboard ---
        st.sidebar.header("⚙️ Opciones del Dashboard")
        
        # Filtro de fecha si el índice es de tipo datetime
        if isinstance(df_actual.index, pd.DatetimeIndex):
            min_date = df_actual.index.min().date()
            max_date = df_actual.index.max().date()
            
            date_range = st.sidebar.date_input(
                "Selecciona un rango de fechas:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                # Asegurarse de que el orden es correcto
                start_date = min(date_range)
                end_date = max(date_range)
                df_filtrado = df_actual.loc[str(start_date):str(end_date)]
                st.sidebar.info(f"Datos filtrados del {start_date} al {end_date}.")
            else:
                df_filtrado = df_actual # No hay filtro si no se seleccionan 2 fechas
        else:
            df_filtrado = df_actual # No hay filtro de fecha si no es índice de fecha

        # Mostrar el DataFrame filtrado (opcional, para depuración o confirmación)
        # st.subheader("Vista Previa de Datos Filtrados")
        # st.dataframe(df_filtrado)


        # --- Sección de Visualización Dinámica ---
        st.subheader("📊 Visualización Dinámica de Datos")

        # Obtener columnas numéricas y categóricas
        columnas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
        columnas_categoricas = df_filtrado.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        
        # Añadir el índice como una opción si es de tipo numérico o si queremos usarlo
        if isinstance(df_filtrado.index, (pd.Int64Index, pd.Float64Index)):
            columnas_numericas.insert(0, df_filtrado.index.name if df_filtrado.index.name else "Índice Numérico")
        elif isinstance(df_filtrado.index, pd.DatetimeIndex):
             # Si el índice es de fecha, podemos considerarlo para el eje X en gráficos de línea/área
             pass # Ya se maneja directamente con st.line_chart o plotear por el índice

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
                if isinstance(df_filtrado.index, pd.DatetimeIndex):
                    st.line_chart(df_filtrado)
                else:
                    st.warning("Este gráfico requiere un índice de fecha/hora para mostrar series de tiempo.")
                    st.dataframe(df_filtrado) # Mostrar datos si no hay índice de fecha
            
            elif chart_type == "Histograma":
                if columnas_numericas:
                    hist_column = st.selectbox("Selecciona columna para Histograma:", options=columnas_numericas, key="hist_col_dyn")
                    if hist_column:
                        fig_hist = px.histogram(df_filtrado, x=hist_column, marginal="rug", title=f"Distribución de {hist_column}")
                        st.plotly_chart(fig_hist)
                else:
                    st.info("No hay columnas numéricas para generar histogramas.")

            elif chart_type == "Gráfico de Dispersión (Scatter)":
                if len(columnas_numericas) >= 2:
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
                    st.info("Necesitas al menos dos columnas numéricas para este gráfico.")
            
            elif chart_type == "Gráfico de Barras":
                if columnas_numericas and (columnas_categoricas or isinstance(df_filtrado.index, (pd.Int64Index, pd.DatetimeIndex))):
                    col1, col2 = st.columns(2)
                    with col1:
                        bar_x = st.selectbox("Eje X (Categoría/Etiqueta):", options=columnas_categoricas + ([df_filtrado.index.name] if df_filtrado.index.name else []), key="bar_x_dyn")
                    with col2:
                        bar_y = st.selectbox("Eje Y (Valor Numérico):", options=columnas_numericas, key="bar_y_dyn")
                    
                    if bar_x and bar_y:
                        fig_bar = px.bar(df_filtrado, x=bar_x, y=bar_y, title=f"Gráfico de Barras de {bar_y} por {bar_x}")
                        st.plotly_chart(fig_bar)
                else:
                    st.info("Necesitas columnas numéricas y categóricas (o un índice apropiado) para este gráfico.")

            elif chart_type == "Box Plot":
                if columnas_numericas:
                    box_y = st.selectbox("Variable a analizar (Eje Y):", options=columnas_numericas, key="box_y_dyn")
                    box_x_cat = st.selectbox("Categoría para agrupar (Eje X, opcional):", options=["Ninguno"] + columnas_categoricas, key="box_x_dyn")
                    
                    if box_y:
                        fig_box = px.box(df_filtrado, y=box_y, x=box_x_cat if box_x_cat != "Ninguno" else None, title=f"Box Plot de {box_y}")
                        st.plotly_chart(fig_box)
                else:
                    st.info("No hay columnas numéricas para generar Box Plots.")

            elif chart_type == "Violin Plot":
                if columnas_numericas:
                    violin_y = st.selectbox("Variable a analizar (Eje Y):", options=columnas_numericas, key="violin_y_dyn")
                    violin_x_cat = st.selectbox("Categoría para agrupar (Eje X, opcional):", options=["Ninguno"] + columnas_categoricas, key="violin_x_dyn")
                    
                    if violin_y:
                        fig_violin = px.violin(df_filtrado, y=violin_y, x=violin_x_cat if violin_x_cat != "Ninguno" else None, title=f"Violin Plot de {violin_y}")
                        st.plotly_chart(fig_violin)
                else:
                    st.info("No hay columnas numéricas para generar Violin Plots.")

            elif chart_type == "Gráfico de Correlación (Heatmap)":
                if not numeric_df.empty: # Usar numeric_df de df_actual antes de filtrar para la correlación general
                    try:
                        fig = px.imshow(numeric_df.corr(), text_auto=True, title="Matriz de Correlación")
                        st.plotly_chart(fig)
                    except Exception as e:
                        st.warning(f"No se pudo generar el gráfico de correlación. Asegúrate de tener al menos dos columnas numéricas. Error: {e}")
                else:
                    st.warning("El DataFrame no contiene columnas numéricas para generar un gráfico de correlación.")

        else:
            st.warning("El DataFrame actual está vacío o no tiene datos después del filtrado.")

        # --- Sección de Exportación ---
        st.subheader("📤 Exportar Datos")
        
        # Generar los datos para la descarga solo si df_actual no está vacío
        pdf_data = generar_pdf(df_filtrado) # Exportar el DataFrame filtrado
        word_data = generar_word(df_filtrado) # Exportar el DataFrame filtrado

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

    if st.button("Cerrar sesión"):
        logout()

# ... (Tu código existente: inicialización, main) ...
