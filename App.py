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

    if df_to_export.empty:
        pdf.cell(200, 10, txt="No hay datos para mostrar en este reporte.", ln=True, align="C")
    else:
        # Calcular el número total de columnas incluyendo el índice si es relevante
        num_cols_display = len(df_to_export.columns)
        include_index_col = False
        # Considerar el índice si tiene nombre o no es el RangeIndex por defecto
        if df_to_export.index.name or not isinstance(df_to_export.index, pd.RangeIndex):
            include_index_col = True
            num_cols_display += 1

        # Asegurar que num_cols_display no sea cero
        if num_cols_display == 0:
            pdf.cell(200, 10, txt="No hay columnas para mostrar.", ln=True, align="C")
        else:
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
    
    if df_to_export.empty:
        doc.add_paragraph("No hay datos para mostrar en este reporte.")
    else:
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

    # Inicializar df_actual como un DataFrame vacío si no hay uno en session_state
    if 'df_cargado' not in st.session_state or st.session_state.df_cargado is None:
        st.session_state.df_cargado = pd.DataFrame()
    
    df_actual = st.session_state.df_cargado
    df_filtrado = df_actual.copy() # df_filtrado siempre empieza como una copia de df_actual

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
            df_filtrado = df_actual.copy() # Actualizar df_filtrado también al cargar nuevo archivo

        except Exception as e:
            st.error(f"Error al leer el archivo CSV: {e}")
            st.info("Asegúrate de que el archivo es un CSV válido y no está dañado.")
            st.session_state.df_cargado = pd.DataFrame() # Asegurar que sea un DataFrame vacío en caso de error
            df_actual = pd.DataFrame()
            df_filtrado = pd.DataFrame()

    # Mostrar la sección de herramientas solo si hay datos en df_actual
    if not df_actual.empty:
        # --- Controles Globales del Dashboard ---
        st.sidebar.header("⚙️ Opciones del Dashboard")
        
        # Filtro de fecha si el índice es de tipo datetime
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
        # Se asegura que numeric_df se crea del df_filtrado actualizado
        numeric_df = df_filtrado.select_dtypes(include=['number']) 
        columnas_numericas = numeric_df.columns.tolist()
        columnas_categoricas = df_filtrado.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        
        # Añadir el índice como una opción si es de tipo numérico o si queremos usarlo para plotear
        if isinstance(df_filtrado.index, (pd.Int64Index, pd.Float64Index)):
            # Asegúrate de que el nombre del índice no sea None antes de añadirlo
            index_name_for_select = df_filtrado.index.name if df_filtrado.index.name else "Índice Numérico"
            if index_name_for_select not in columnas_numericas: # Evitar duplicados
                columnas_numericas.insert(0, index_name_for_select)


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
                    if not df_filtrado.empty: st.dataframe(df_filtrado) 
            
            elif chart_type == "Histograma":
                if columnas_numericas and not df_filtrado.empty:
                    hist_column = st.selectbox("Selecciona columna para Histograma:", options=columnas_numericas, key="hist_col_dyn")
                    if hist_column:
                        # Si la columna seleccionada es el índice numérico
                        if hist_column == (df_filtrado.index.name or "Índice Numérico") and isinstance(df_filtrado.index, (pd.Int64Index, pd.Float64Index)):
                            data_to_plot = df_filtrado.index
                        else:
                            data_to_plot = df_filtrado[hist_column]

                        fig_hist = px.histogram(df_filtrado, x=data_to_plot, marginal="rug", title=f"Distribución de {hist_column}")
                        st.plotly_chart(fig_hist)
                else:
                    st.info("No hay columnas numéricas o datos para generar histogram
            
