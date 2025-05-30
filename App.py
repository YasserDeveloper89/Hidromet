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

    # Añadir los encabezados de las columnas
    # Calcular el ancho de la columna dinámicamente para el índice y las columnas de datos
    num_cols = len(df_to_export.columns)
    # Si el índice tiene nombre o se va a mostrar, cuenta como una columna más
    if df_to_export.index.name or not df_to_export.index.is_unique or isinstance(df_to_export.index, pd.RangeIndex):
        num_cols += 1 
    
    col_width = pdf.w / num_cols 
    
    # Añadir el encabezado del índice
    if df_to_export.index.name:
        pdf.cell(col_width, 10, str(df_to_export.index.name), border=1)
    else:
        # Si el índice no tiene nombre y no es un RangeIndex (por defecto 0, 1, 2...), darle un nombre genérico
        if not isinstance(df_to_export.index, pd.RangeIndex):
            pdf.cell(col_width, 10, "Índice", border=1)
        else:
            # Si es un RangeIndex, no imprimimos "Índice" a menos que haya un nombre explícito
            # O ajustamos el num_cols para que no considere el índice si es default
            num_cols -= 1 # Reajustar si el índice es un RangeIndex y no se mostrará explícitamente como "Índice"
            col_width = pdf.w / num_cols # Recalcular el ancho de la columna
            # No imprimir la celda del índice para RangeIndex sin nombre
            pass


    for col in df_to_export.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()

    # Añadir los datos
    for index, row in df_to_export.iterrows():
        # Manejar el índice, especialmente si es un Timestamp
        if df_to_export.index.name or not isinstance(df_to_export.index, pd.RangeIndex):
            if isinstance(index, pd.Timestamp):
                pdf.cell(col_width, 10, str(index.strftime('%Y-%m-%d')), border=1)
            else:
                pdf.cell(col_width, 10, str(index), border=1)
        
        # Añadir los valores de las filas
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    buffer = BytesIO()
    # **AQUÍ ESTÁ LA MODIFICACIÓN CLAVE: .encode('latin-1')**
    pdf_data = pdf.output(dest='S').encode('latin-1') 
    buffer.write(pdf_data)
    buffer.seek(0) # Retroceder al inicio del buffer antes de devolverlo
    
    return buffer.getvalue()

# ----------------- Generar Word -----------------
def generar_word(df_to_export):
    doc = Document()
    doc.add_heading("Reporte de Datos", 0)
    
    # Asegúrate de incluir el nombre del índice si existe, o una columna de "Índice"
    columns_for_word = []
    # Añadir el encabezado del índice si es relevante
    if df_to_export.index.name:
        columns_for_word.append(df_to_export.index.name)
    elif not isinstance(df_to_export.index, pd.RangeIndex):
        columns_for_word.append("Índice")
    
    columns_for_word.extend(df_to_export.columns.tolist())

    table = doc.add_table(rows=1, cols=len(columns_for_word))
    hdr_cells = table.rows[0].cells
    for i, col_name in enumerate(columns_for_word):
        hdr_cells[i].text = col_name
    
    for index, row in df_to_export.iterrows():
        row_cells = table.add_row().cells
        cell_idx = 0

        # Añadir el índice si es relevante
        if df_to_export.index.name or not isinstance(df_to_export.index, pd.RangeIndex):
            if isinstance(index, pd.Timestamp):
                row_cells[cell_idx].text = str(index.strftime('%Y-%m-%d'))
            else:
                row_cells[cell_idx].text = str(index)
            cell_idx += 1

        # Añadir los valores de las columnas del DataFrame
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

    if uploaded_file is None:
        st.session_state.df_cargado = None

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Archivo CSV cargado exitosamente.")

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
    
    df_actual = st.session_state.df_cargado

    if df_actual is not None and not df_actual.empty:
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
        
        # Generar los datos para la descarga solo si df_actual no está vacío
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
            
