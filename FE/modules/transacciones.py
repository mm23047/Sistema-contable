"""
Página Streamlit para gestionar Transacciones.
Proporciona formularios para crear, editar y listar transacciones.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
from typing import Optional

def render_page(backend_url: str):
    """Renderizar la página de gestión de transacciones"""
    st.header("📋 Gestión de Transacciones")
    
    # Crear formulario de transacciones
    with st.expander("➕ Crear Nueva Transacción", expanded=True):
        create_transaction_form(backend_url)
    
    st.markdown("---")
    
    # Listar transacciones existentes
    st.subheader("📊 Lista de Transacciones")
    list_transactions(backend_url)

def create_transaction_form(backend_url: str):
    """Formulario para crear una nueva transacción"""
    with st.form("create_transaction"):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_transaccion = st.date_input(
                "Fecha de Transacción",
                value=date.today(),
                help="Fecha cuando ocurrió la transacción"
            )
            
            tipo = st.selectbox(
                "Tipo de Transacción",
                ["INGRESO", "EGRESO"],
                help="Tipo de transacción contable"
            )
            
            usuario_creacion = st.text_input(
                "Usuario",
                placeholder="Nombre del usuario",
                help="Usuario que crea la transacción"
            )
        
        with col2:
            descripcion = st.text_area(
                "Descripción",
                placeholder="Descripción detallada de la transacción...",
                height=100,
                help="Descripción completa de la transacción"
            )
            
            moneda = st.selectbox(
                "Moneda",
                ["USD", "EUR", "MXN", "COP"],
                index=0,
                help="Moneda de la transacción"
            )
            
            # TODO: Cargar períodos desde la API
            id_periodo = st.number_input(
                "ID Período (requerido)",
                min_value=1,
                value=1,
                help="ID del período contable asociado (requerido)"
            )
        
        submitted = st.form_submit_button("Crear Transacción", type="primary")
        
        if submitted:
            if not descripcion or not usuario_creacion:
                st.error("❌ Descripción y Usuario son campos obligatorios")
                return
            
            # Combine date with current time for datetime
            fecha_datetime = datetime.combine(fecha_transaccion, datetime.now().time())
            
            # Prepare request data
            transaction_data = {
                "fecha_transaccion": fecha_datetime.isoformat(),
                "descripcion": descripcion,
                "tipo": tipo,
                "moneda": moneda,
                "usuario_creacion": usuario_creacion,
                "id_periodo": id_periodo
            }
            
            try:
                response = requests.post(
                    f"{backend_url}/api/transacciones/",
                    json=transaction_data,
                    timeout=10
                )
                
                if response.status_code == 201:
                    data = response.json()
                    transaction_id = data.get("id_transaccion")
                    
                    # Set current transaction in session state
                    st.session_state.transaccion_actual = transaction_id
                    
                    st.success(f"✅ Transacción creada exitosamente (ID: {transaction_id})")
                    st.info("💡 Ahora puedes crear asientos para esta transacción")
                    st.rerun()
                else:
                    st.error(f"❌ Error al crear transacción: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error de conexión: {str(e)}")

def list_transactions(backend_url: str):
    """Listar transacciones existentes en una tabla"""
    try:
        response = requests.get(f"{backend_url}/api/transacciones/", timeout=10)
        
        if response.status_code == 200:
            transactions = response.json()
            
            if not transactions:
                st.info("📭 No hay transacciones registradas")
                return
            
            # Convert to DataFrame for display
            df = pd.DataFrame(transactions)
            
            # Format datetime columns
            if not df.empty:
                try:
                    # Use mixed format to handle different datetime formats automatically
                    df['fecha_transaccion'] = pd.to_datetime(df['fecha_transaccion'], format='mixed').dt.strftime('%Y-%m-%d %H:%M')
                    df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion'], format='mixed').dt.strftime('%Y-%m-%d %H:%M')
                except:
                    # Fallback: try without specifying format (pandas will infer)
                    df['fecha_transaccion'] = pd.to_datetime(df['fecha_transaccion'], infer_datetime_format=True).dt.strftime('%Y-%m-%d %H:%M')
                    df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion'], infer_datetime_format=True).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display table
            st.dataframe(
                df[['id_transaccion', 'fecha_transaccion', 'descripcion', 'tipo', 'moneda', 'usuario_creacion']],
                use_container_width=True
            )
            
            # Action buttons for each transaction
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_id = st.selectbox(
                    "Seleccionar Transacción",
                    options=[None] + [t['id_transaccion'] for t in transactions],
                    format_func=lambda x: "Selecciona..." if x is None else f"ID: {x}"
                )
            
            with col2:
                if st.button("🎯 Usar para Asientos") and selected_id:
                    st.session_state.transaccion_actual = selected_id
                    st.success(f"✅ Transacción {selected_id} seleccionada")
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Eliminar") and selected_id:
                    delete_transaction(backend_url, selected_id)
        else:
            st.error(f"❌ Error al cargar transacciones: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")

def delete_transaction(backend_url: str, transaction_id: int):
    """Eliminar una transacción"""
    try:
        response = requests.delete(f"{backend_url}/api/transacciones/{transaction_id}", timeout=10)
        
        if response.status_code == 204:
            st.success(f"✅ Transacción {transaction_id} eliminada")
            # Clear from session if it was the current one
            if st.session_state.transaccion_actual == transaction_id:
                st.session_state.transaccion_actual = None
            st.rerun()
        else:
            st.error(f"❌ Error al eliminar transacción: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")