"""
Página Streamlit para generar y visualizar reportes.
Proporciona acceso al Libro Diario y funcionalidad de exportación.
"""
import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from typing import Optional, List, Dict

def load_periods(backend_url: str):
    """Cargar períodos disponibles desde la API"""
    try:
        response = requests.get(f"{backend_url}/api/periodos/activos", timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Error al cargar períodos: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión al cargar períodos: {str(e)}")
        return []

def render_page(backend_url: str):
    """Renderizar la página de reportes"""
    st.header("📊 Reportes Contables")
    
    # Report navigation tabs
    tab1, tab2, tab3 = st.tabs(["📋 Libro Diario", "💾 Exportaciones", "⚖️ Balance"])
    
    with tab1:
        show_libro_diario(backend_url)
    
    with tab2:
        show_export_options(backend_url)
    
    with tab3:
        show_balance_report(backend_url)

def show_libro_diario(backend_url: str):
    """Mostrar el Libro Diario (General Journal)"""
    st.subheader("📋 Libro Diario")
    
    # Cargar períodos disponibles
    periods = load_periods(backend_url)
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Selector de período mejorado
        if periods:
            # Agregar opción "Todos los períodos" al inicio
            period_options = {"Todos los períodos": None}
            for period in periods:
                display_text = f"{period['tipo_periodo']} {period['fecha_inicio']} - {period['fecha_fin']} (ID: {period['id_periodo']})"
                period_options[display_text] = period['id_periodo']
            
            selected_period_display = st.selectbox(
                "Filtrar por Período",
                options=list(period_options.keys()),
                help="Selecciona el período contable para filtrar los asientos"
            )
            selected_period_id = period_options[selected_period_display]
        else:
            st.error("❌ No se pudieron cargar los períodos disponibles")
            selected_period_id = None
    
    with col2:
        if st.button("🔍 Cargar Libro Diario", type="primary"):
            load_libro_diario(backend_url, selected_period_id)

def load_libro_diario(backend_url: str, periodo_id: Optional[int] = None):
    """Cargar y mostrar los datos del Libro Diario"""
    try:
        params = {}
        if periodo_id:
            params["periodo_id"] = periodo_id
        
        response = requests.get(
            f"{backend_url}/api/reportes/libro-diario",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                st.info("📭 No hay datos para mostrar en el libro diario")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Format datetime column
            df['fecha_transaccion'] = pd.to_datetime(df['fecha_transaccion']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display summary metrics
            total_debe = df['debe'].sum()
            total_haber = df['haber'].sum()
            total_entries = len(df)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Asientos", total_entries)
            with col2:
                st.metric("💰 Total Débitos", f"${total_debe:,.2f}")
            with col3:
                st.metric("💰 Total Créditos", f"${total_haber:,.2f}")
            
            # Display data table
            st.dataframe(
                df[['fecha_transaccion', 'descripcion', 'tipo_transaccion', 
                   'codigo_cuenta', 'nombre_cuenta', 'debe', 'haber']],
                use_container_width=True
            )
            
            # Balance validation
            if abs(total_debe - total_haber) > 0.01:  # Allow for small floating point differences
                st.error("⚠️ ATENCIÓN: El libro diario no está balanceado. Revisa los asientos.")
            else:
                st.success("✅ El libro diario está correctamente balanceado.")
        
        else:
            st.error(f"❌ Error al cargar libro diario: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")

def show_export_options(backend_url: str):
    """Mostrar opciones de exportación para reportes"""
    st.subheader("💾 Exportar Reportes")
    
    # Cargar períodos disponibles
    periods = load_periods(backend_url)
    
    # Export form
    with st.form("export_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "Formato de Exportación",
                ["excel", "html"],
                help="Selecciona el formato para exportar"
            )
        
        with col2:
            # Selector de período mejorado
            if periods:
                # Agregar opción "Todos los períodos" al inicio
                period_options = {"Todos los períodos": None}
                for period in periods:
                    display_text = f"{period['tipo_periodo']} {period['fecha_inicio']} - {period['fecha_fin']} (ID: {period['id_periodo']})"
                    period_options[display_text] = period['id_periodo']
                
                selected_period_display = st.selectbox(
                    "Filtrar por Período (opcional)",
                    options=list(period_options.keys()),
                    help="Selecciona el período contable para filtrar el reporte"
                )
                selected_period_id = period_options[selected_period_display]
            else:
                st.error("❌ No se pudieron cargar los períodos disponibles")
                selected_period_id = None
        
        submitted = st.form_submit_button("📥 Generar Reporte", type="primary")
        
        if submitted:
            generate_report_file(backend_url, export_format, selected_period_id)
    
    # Show download button outside the form if file is ready
    if 'report_file_data' in st.session_state and 'report_file_info' in st.session_state:
        file_data = st.session_state.report_file_data
        file_info = st.session_state.report_file_info
        
        st.success(f"✅ Archivo {file_info['format'].upper()} generado exitosamente")
        
        # Download button outside of form
        st.download_button(
            label=f"📥 Descargar {file_info['format'].upper()}",
            data=file_data,
            file_name=file_info['filename'],
            mime=file_info['mime_type'],
            type="primary"
        )
        
        # Clear button to reset
        if st.button("🔄 Generar Nuevo Reporte"):
            if 'report_file_data' in st.session_state:
                del st.session_state.report_file_data
            if 'report_file_info' in st.session_state:
                del st.session_state.report_file_info
            st.rerun()

def generate_report_file(backend_url: str, format_type: str, periodo_id: Optional[int] = None):
    """Generar archivo de reporte y guardarlo en session_state"""
    try:
        params = {"format": format_type}
        if periodo_id:
            params["periodo_id"] = periodo_id
        
        # Show loading message
        with st.spinner(f"Generando reporte en formato {format_type.upper()}..."):
            response = requests.get(
                f"{backend_url}/api/reportes/libro-diario/export",
                params=params,
                timeout=30  # Longer timeout for file generation
            )
        
        if response.status_code == 200:
            # Determine file extension and MIME type
            if format_type == "excel":
                file_ext = "xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                file_ext = "html"
                mime_type = "text/html"
            
            # Store file data in session state
            st.session_state.report_file_data = response.content
            st.session_state.report_file_info = {
                'format': format_type,
                'filename': f"libro_diario.{file_ext}",
                'mime_type': mime_type
            }
            
            st.rerun()  # Refresh to show download button
        
        else:
            st.error(f"❌ Error al generar exportación: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")

def show_balance_report(backend_url: str):
    """Mostrar reporte de balance por período"""
    st.subheader("⚖️ Balance por Período")
    
    # Cargar períodos disponibles
    periods = load_periods(backend_url)
    
    # Period selection
    if periods:
        period_options = {}
        for period in periods:
            display_text = f"{period['tipo_periodo']} {period['fecha_inicio']} - {period['fecha_fin']} (ID: {period['id_periodo']})"
            period_options[display_text] = period['id_periodo']
        
        selected_period_display = st.selectbox(
            "Período para Balance",
            options=list(period_options.keys()),
            help="Selecciona el período contable para generar el balance (requerido)"
        )
        selected_period_id = period_options[selected_period_display]
        
        # Botón centrado debajo del selector
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📊 Generar Balance", type="primary", use_container_width=True):
                load_balance_report(backend_url, selected_period_id)
    else:
        st.error("❌ No se pudieron cargar los períodos disponibles")
        selected_period_id = None

def load_balance_report(backend_url: str, periodo_id: int):
    """Cargar y mostrar reporte de balance"""
    try:
        response = requests.get(
            f"{backend_url}/api/reportes/balance",
            params={"periodo_id": periodo_id},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            cuentas = data.get("cuentas", [])
            totales = data.get("totales", {})
            
            if not cuentas:
                st.info(f"📭 No hay datos de balance para el período {periodo_id}")
                return
            
            # Display period info (centered)
            st.markdown(f"<h3 style='text-align: center;'>📅 Balance para Período ID: {periodo_id}</h3>", unsafe_allow_html=True)
            
            # Convert to DataFrame
            df = pd.DataFrame(cuentas)
            
            # Display balance by account type (centered)
            for tipo_cuenta in df['tipo_cuenta'].unique():
                # Título centrado más grande
                st.markdown(f"<h2 style='text-align: center;'>{tipo_cuenta}</h2>", unsafe_allow_html=True)
                tipo_df = df[df['tipo_cuenta'] == tipo_cuenta]
                
                # Preparar columnas para mostrar
                column_mapping = {
                    'codigo_cuenta': 'Código',
                    'nombre_cuenta': 'Nombre Cuenta', 
                    'total_debe': 'Total Débito',
                    'total_haber': 'Total Crédito',
                    'saldo': 'Saldo'
                }
                
                # Seleccionar solo las columnas que existen en los datos
                available_columns = [col for col in column_mapping.keys() if col in tipo_df.columns]
                
                if available_columns:
                    # Renombrar columnas para mejor visualización
                    display_df = tipo_df[available_columns].copy()
                    display_df.columns = [column_mapping[col] for col in available_columns]
                    
                    # Tabla centrada y más grande
                    col_left, col_center, col_right = st.columns([0.5, 4, 0.5])
                    with col_center:
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            height=(len(tipo_df) + 1) * 35 + 3,
                            hide_index=False
                        )
            
            # Display totals (centered)
            st.markdown("---")
            col_space1, col1, col2, col_space2 = st.columns([1, 2, 2, 1])
            
            with col1:
                total_debe = totales.get('total_debe', 0)
                st.metric("💰 Total Débitos", f"${total_debe:,.2f}")
            
            with col2:
                total_haber = totales.get('total_haber', 0)
                st.metric("💰 Total Créditos", f"${total_haber:,.2f}")
            
            # Balance validation
            difference = total_debe - total_haber
            if abs(difference) > 0.01:
                st.error(f"⚠️ ATENCIÓN: Balance desbalanceado por ${difference:,.2f}")
            else:
                st.success("✅ Balance correctamente balanceado.")
        
        else:
            st.error(f"❌ Error al cargar balance: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")