"""
Página Streamlit para gestionar Transacciones.
Proporciona formularios para crear, editar y listar transacciones.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

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
    """Renderizar la página de gestión de transacciones"""
    st.header("📋 Gestión de Transacciones")
    
    # Crear formulario de transacciones
    with st.expander("➕ Crear Nueva Transacción", expanded=True):
        create_transaction_form(backend_url)
    
    # Formulario de edición (solo si hay una transacción seleccionada para editar)
    if 'edit_transaction_id' in st.session_state and 'edit_transaction_data' in st.session_state:
        with st.expander("✏️ Modificar Transacción", expanded=True):
            edit_transaction_form(backend_url)
    
    st.markdown("---")
    
    # Listar transacciones existentes
    st.subheader("📊 Lista de Transacciones")
    list_transactions(backend_url)


# (CÓDIGO ORIGINAL OMITIDO ARRIBA PARA NO REPETIR)
# ─────────────────────────────────────────────────────────
# SOLO DESDE create_transaction_form HACIA ABAJO
# ─────────────────────────────────────────────────────────

def create_transaction_form(backend_url: str):
    """Formulario para crear una nueva transacción"""
    periods = load_periods(backend_url)

    with st.form("create_transaction"):
        col1, col2 = st.columns(2)

        with col1:
            fecha_transaccion = st.date_input(
                "Fecha de Transacción",
                value=date.today(),
            )

            tipo = st.selectbox("Tipo de Transacción", ["INGRESO", "EGRESO"])

            usuario_creacion = st.text_input(
                "Usuario",
                placeholder="Nombre del usuario"
            )

        with col2:
            descripcion = st.text_area(
                "Descripción",
                placeholder="Descripción detallada..."
            )

            moneda = st.selectbox("Moneda", ["USD", "EUR", "MXN", "COP"])

            categoria = st.selectbox(
                "Tipo de Categoria",
                ["VENTA", "COMPRA", "SERVICIO", "OTROS"]
            )

            # PERIODOS
            if periods:
                period_options = {
                    f"{p['tipo_periodo']} {p['fecha_inicio']} - {p['fecha_fin']} (ID: {p['id_periodo']})": p[
                        'id_periodo']
                    for p in periods
                }
                selected_period_display = st.selectbox(
                    "Período Contable",
                    list(period_options.keys())
                )
                selected_period_id = period_options[selected_period_display]
            else:
                st.error("❌ No se pudieron cargar los períodos")
                selected_period_id = None

        submitted = st.form_submit_button("Crear Transacción", type="primary")

        if submitted:
            if not descripcion or not usuario_creacion:
                st.error("❌ Descripción y Usuario son obligatorios")
                return

            if not selected_period_id:
                st.error("❌ No se pudo seleccionar período")
                return

            fecha_datetime = datetime.combine(fecha_transaccion, datetime.now().time())

            transaction_data = {
                "fecha_transaccion": fecha_datetime.isoformat(),
                "descripcion": descripcion,
                "tipo": tipo,
                "moneda": moneda,
                "usuario_creacion": usuario_creacion,
                "id_periodo": selected_period_id,
                "categoria": categoria
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

                    st.session_state.transaccion_actual = transaction_id

                    st.success(f"✅ Transacción creada (ID: {transaction_id})")
                    st.info("💡 Ahora puedes crear asientos para esta transacción")
                    st.rerun()

                else:
                    st.error(f"❌ Error al crear transacción: {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error de conexión: {str(e)}")


def edit_transaction_form(backend_url: str):
    """Formulario para modificar una transacción existente"""
    transaction_data = st.session_state.edit_transaction_data
    transaction_id = st.session_state.edit_transaction_id
    
    # Cargar períodos para mostrar información descriptiva
    periods = load_periods(backend_url)
    
    st.info(f"🔄 Modificando Transacción ID: {transaction_id}")
    
    # Botón para cancelar edición
    if st.button("❌ Cancelar Edición"):
        if 'edit_transaction_id' in st.session_state:
            del st.session_state.edit_transaction_id
        if 'edit_transaction_data' in st.session_state:
            del st.session_state.edit_transaction_data
        st.rerun()
    
    with st.form("edit_transaction"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Parse the existing date from ISO format
            try:
                existing_date = datetime.fromisoformat(transaction_data['fecha_transaccion'].replace('Z', '+00:00'))
            except (ValueError, KeyError):
                # Fallback to current date if parsing fails
                existing_date = datetime.now()
            
            fecha_transaccion = st.date_input(
                "Fecha de Transacción",
                value=existing_date.date(),
                help="Fecha cuando ocurrió la transacción"
            )
            
            tipo = st.selectbox(
                "Tipo de Transacción",
                ["INGRESO", "EGRESO"],
                index=0 if transaction_data.get('tipo') == 'INGRESO' else 1,
                help="Tipo de transacción contable"
            )
            
            usuario_creacion = st.text_input(
                "Usuario",
                value=transaction_data.get('usuario_creacion', ''),
                help="Usuario que crea la transacción"
            )
        
        with col2:
            descripcion = st.text_area(
                "Descripción",
                value=transaction_data.get('descripcion', ''),
                height=100,
                help="Descripción completa de la transacción"
            )

            categoria = st.selectbox(
                "Tipo de Categoria",
                ["VENTA", "COMPRA", "SERVICIO", "OTROS"],
                index=0 if transaction_data.get('categoria') == 'VENTA' else 1,
                help="Tipo de categoria"
            )
            
            # List of common currencies with current value selected
            currencies = ["USD", "EUR", "MXN", "COP"]
            current_currency = transaction_data.get('moneda', 'USD')
            currency_index = currencies.index(current_currency) if current_currency in currencies else 0
            
            moneda = st.selectbox(
                "Moneda",
                currencies,
                index=currency_index,
                help="Moneda de la transacción"
            )
            
            # Display current period information in a more user-friendly way
            current_period_id = transaction_data.get('id_periodo', 'N/A')
            if periods and current_period_id != 'N/A':
                # Find the current period in the list
                current_period = next((p for p in periods if p['id_periodo'] == current_period_id), None)
                if current_period:
                    period_display = f"{current_period['tipo_periodo']} {current_period['fecha_inicio']} - {current_period['fecha_fin']}"
                    st.info(f"📅 Período actual: {period_display} (ID: {current_period_id})")
                else:
                    st.info(f"📅 Período actual: ID {current_period_id} (no encontrado en períodos activos)")
            else:
                st.info(f"📅 Período actual: ID {current_period_id}")
        
        submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
        
        if submitted:
            if not descripcion or not usuario_creacion:
                st.error("❌ Descripción y Usuario son campos obligatorios")
                return
            
            # Combine date with existing time for datetime
            existing_time = existing_date.time()
            fecha_datetime = datetime.combine(fecha_transaccion, existing_time)
            
            # Prepare update data - only include fields that can be modified
            update_data = {
                "fecha_transaccion": fecha_datetime.isoformat(),
                "descripcion": descripcion,
                "tipo": tipo,
                "moneda": moneda,
                "usuario_creacion": usuario_creacion,
                "categoria": categoria
                # Note: id_periodo is not included as per requirements
            }
            
            edit_transaction(backend_url, transaction_id, update_data)

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
                df[['id_transaccion', 'fecha_transaccion', 'descripcion', 'tipo', 'moneda', 'usuario_creacion', 'categoria']],
                use_container_width=True
            )
            
            # Action buttons for each transaction
            col1, col2, col3, col4 = st.columns(4)
            
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
                if st.button("✏️ Modificar") and selected_id:
                    # Encontrar la transacción seleccionada para el formulario de edición
                    selected_transaction = next((t for t in transactions if t['id_transaccion'] == selected_id), None)
                    if selected_transaction:
                        st.session_state.edit_transaction_id = selected_id
                        st.session_state.edit_transaction_data = selected_transaction
                        st.rerun()
            
            with col4:
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

def edit_transaction(backend_url: str, transaction_id: int, transaction_data: dict):
    """Modificar una transacción existente"""
    try:
        response = requests.put(
            f"{backend_url}/api/transacciones/{transaction_id}", 
            json=transaction_data, 
            timeout=10
        )
        
        if response.status_code == 200:
            st.success(f"✅ Transacción {transaction_id} modificada exitosamente")
            # Limpiar el estado de edición
            if 'edit_transaction_id' in st.session_state:
                del st.session_state.edit_transaction_id
            if 'edit_transaction_data' in st.session_state:
                del st.session_state.edit_transaction_data
            st.rerun()
        else:
            st.error(f"❌ Error al modificar transacción: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")