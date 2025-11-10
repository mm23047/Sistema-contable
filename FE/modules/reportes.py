"""
Página Streamlit para generar y visualizar reportes.
Proporciona acceso al Libro Diario y funcionalidad de exportación.
"""
import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from typing import Optional, List, Dict

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
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        # TODO: Cargar períodos reales desde la API
        periodo_id = st.number_input(
            "Filtrar por Período (opcional)",
            min_value=0,
            value=0,
            help="ID del período contable para filtrar. 0 = todos los períodos"
        )
    
    with col2:
        if st.button("🔍 Cargar Libro Diario", type="primary"):
            load_libro_diario(backend_url, periodo_id if periodo_id > 0 else None)

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
            # TODO: Cargar períodos reales desde la API
            periodo_id = st.number_input(
                "Filtrar por Período (opcional)",
                min_value=0,
                value=0,
                help="ID del período contable para filtrar. 0 = todos los períodos"
            )
        
        submitted = st.form_submit_button("📥 Generar y Descargar", type="primary")
        
        if submitted:
            export_report(backend_url, export_format, periodo_id if periodo_id > 0 else None)

def export_report(backend_url: str, format_type: str, periodo_id: Optional[int] = None):
    """Exportar reporte en el formato especificado"""
    try:
        params = {"format": format_type}
        if periodo_id:
            params["periodo_id"] = periodo_id
        
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
            
            # Provide download button
            st.download_button(
                label=f"📥 Descargar {format_type.upper()}",
                data=response.content,
                file_name=f"libro_diario.{file_ext}",
                mime=mime_type,
                type="primary"
            )
            
            st.success(f"✅ Archivo {format_type.upper()} generado exitosamente")
        
        else:
            st.error(f"❌ Error al generar exportación: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")

def show_balance_report(backend_url: str):
    """Mostrar reporte de balance por período"""
    st.subheader("⚖️ Balance por Período")
    
    # Period selection
    col1, col2 = st.columns(2)
    
    with col1:
        # TODO: Cargar períodos reales desde la API y crear selectbox
        periodo_id = st.number_input(
            "Período para Balance",
            min_value=1,
            value=1,
            help="ID del período contable para generar balance"
        )
    
    with col2:
        if st.button("📊 Generar Balance", type="primary"):
            load_balance_report(backend_url, periodo_id)

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
            
            # Display period info
            st.info(f"📅 Balance para Período ID: {periodo_id}")
            
            # Convert to DataFrame
            df = pd.DataFrame(cuentas)
            
            # Display balance by account type
            for tipo_cuenta in df['tipo_cuenta'].unique():
                st.markdown(f"### {tipo_cuenta}")
                tipo_df = df[df['tipo_cuenta'] == tipo_cuenta]
                
                st.dataframe(
                    tipo_df[['codigo_cuenta', 'nombre_cuenta', 'total_debe', 'total_haber', 'saldo']],
                    use_container_width=True
                )
            
            # Display totals
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("💰 Total Débitos", f"${totales.get('total_debe', 0):,.2f}")
            
            with col2:
                st.metric("💰 Total Créditos", f"${totales.get('total_haber', 0):,.2f}")
            
            # Balance validation
            difference = totales.get('total_debe', 0) - totales.get('total_haber', 0)
            if abs(difference) > 0.01:
                st.error(f"⚠️ ATENCIÓN: Balance desbalanceado por ${difference:,.2f}")
            else:
                st.success("✅ Balance correctamente balanceado.")
        
        else:
            st.error(f"❌ Error al cargar balance: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")