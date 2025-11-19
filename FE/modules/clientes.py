"""
Página Streamlit para gestionar Clientes.
Proporciona CRUD completo para clientes con búsqueda y estadísticas.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime


def render_page(backend_url: str):
    """Renderizar la página de gestión de clientes"""
    st.title("👥 Gestión de Clientes")
    st.markdown("---")

    # ============================
    # Tabs para diferentes vistas
    # ============================
    tab1, tab2, tab3 = st.tabs(["📋 Listado de Clientes", "➕ Crear/Editar Cliente", "📊 Estadísticas"])

    # ============================
    # TAB 1: LISTADO DE CLIENTES
    # ============================
    with tab1:
        st.subheader("Clientes Registrados")
        
        # Filtros de búsqueda
        col1, col2, col3 = st.columns(3)
        with col1:
            busqueda = st.text_input("🔍 Buscar", placeholder="Nombre, NIT o email...")
        with col2:
            tipo_filtro = st.selectbox("Tipo", ["Todos", "INDIVIDUAL", "EMPRESA"])
        with col3:
            activo_filtro = st.selectbox("Estado", ["Todos", "SI", "NO"])

        # Botón de actualizar
        col_refresh, col_new = st.columns([3, 1])
        with col_refresh:
            if st.button("🔄 Actualizar Lista", use_container_width=True):
                st.rerun()
        with col_new:
            if st.button("➕ Nuevo Cliente", use_container_width=True, type="primary"):
                st.session_state['crear_cliente_activo'] = True
                st.session_state['editar_cliente_id'] = None
                st.rerun()

        # Obtener clientes desde backend
        def get_clientes():
            try:
                params = {}
                if busqueda:
                    params['busqueda'] = busqueda
                if tipo_filtro != "Todos":
                    params['tipo'] = tipo_filtro
                if activo_filtro != "Todos":
                    params['activo'] = activo_filtro
                
                resp = requests.get(f"{backend_url}/api/clientes/", params=params, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                st.error(f"❌ Error obteniendo clientes: {e}")
                return []

        clientes = get_clientes()

        if not clientes:
            st.warning("📭 No hay clientes registrados aún.")
            st.info("💡 Crea tu primer cliente desde la pestaña **➕ Crear/Editar Cliente**")
        else:
            st.success(f"✅ Se encontraron {len(clientes)} cliente(s)")
            st.markdown("---")

            # Mostrar tabla de clientes
            for cliente in clientes:
                with st.expander(
                    f"👤 **{cliente['nombre']}** - {cliente['nit']} - {cliente['tipo_cliente']}", 
                    expanded=False
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID Cliente:** {cliente['id_cliente']}")
                        st.write(f"**Nombre:** {cliente['nombre']}")
                        st.write(f"**NIT:** {cliente['nit']}")
                        st.write(f"**Tipo:** {cliente['tipo_cliente']}")
                        st.write(f"**Activo:** {'✅ Sí' if cliente['activo'] == 'SI' else '❌ No'}")
                    
                    with col2:
                        st.write(f"**Contacto:** {cliente.get('contacto_nombre', 'N/A')}")
                        st.write(f"**Teléfono:** {cliente.get('contacto_telefono', 'N/A')}")
                        st.write(f"**Email:** {cliente.get('contacto_email', 'N/A')}")
                        st.write(f"**Dirección:** {cliente.get('direccion', 'N/A')}")
                        fecha_registro = cliente.get('fecha_registro')
                        if fecha_registro:
                            try:
                                fecha_obj = datetime.fromisoformat(fecha_registro.replace('Z', '+00:00'))
                                fecha_str = fecha_obj.strftime('%d/%m/%Y')
                            except:
                                fecha_str = fecha_registro
                        else:
                            fecha_str = 'N/A'
                        st.write(f"**Fecha Registro:** {fecha_str}")

                    st.markdown("---")
                    
                    # Botones de acción
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(
                            "✏️ Editar", 
                            key=f"edit_{cliente['id_cliente']}", 
                            use_container_width=True
                        ):
                            st.session_state['editar_cliente_id'] = cliente['id_cliente']
                            st.session_state['editar_cliente_data'] = cliente
                            st.session_state['crear_cliente_activo'] = False
                            st.rerun()
                    
                    with col2:
                        if cliente['activo'] == 'SI':
                            if st.button(
                                "🚫 Desactivar", 
                                key=f"deactivate_{cliente['id_cliente']}", 
                                use_container_width=True
                            ):
                                try:
                                    resp = requests.patch(
                                        f"{backend_url}/api/clientes/{cliente['id_cliente']}/desactivar",
                                        timeout=10
                                    )
                                    if resp.status_code == 200:
                                        st.success("✅ Cliente desactivado exitosamente")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Error: {resp.text}")
                                except Exception as e:
                                    st.error(f"❌ Error al desactivar: {e}")
                    
                    with col3:
                        if st.button(
                            "🗑️ Eliminar", 
                            key=f"delete_{cliente['id_cliente']}", 
                            use_container_width=True,
                            type="secondary"
                        ):
                            if st.session_state.get(f"confirm_delete_{cliente['id_cliente']}", False):
                                try:
                                    resp = requests.delete(
                                        f"{backend_url}/api/clientes/{cliente['id_cliente']}",
                                        timeout=10
                                    )
                                    if resp.status_code == 204:
                                        st.success("✅ Cliente eliminado exitosamente")
                                        st.session_state[f"confirm_delete_{cliente['id_cliente']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Error: {resp.json().get('detail', resp.text)}")
                                except Exception as e:
                                    st.error(f"❌ Error al eliminar: {e}")
                            else:
                                st.session_state[f"confirm_delete_{cliente['id_cliente']}"] = True
                                st.warning("⚠️ Haz clic nuevamente para confirmar eliminación")

    # ============================
    # TAB 2: CREAR/EDITAR CLIENTE
    # ============================
    with tab2:
        # Determinar si estamos editando
        editando = st.session_state.get('editar_cliente_id') is not None
        datos_edicion = st.session_state.get('editar_cliente_data', {})

        if editando:
            st.subheader(f"✏️ Editar Cliente: {datos_edicion.get('nombre', '')}")
        else:
            st.subheader("➕ Crear Nuevo Cliente")

        with st.form("form_cliente"):
            st.markdown("#### 📋 Información General")
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input(
                    "Nombre del Cliente *", 
                    value=datos_edicion.get('nombre', ''),
                    placeholder="Ej: CORPORACIÓN XYZ S.A."
                )
                nit = st.text_input(
                    "NIT *", 
                    value=datos_edicion.get('nit', ''),
                    placeholder="0614-120190-101-2"
                )
                tipo_cliente = st.selectbox(
                    "Tipo de Cliente *",
                    ["INDIVIDUAL", "EMPRESA"],
                    index=0 if datos_edicion.get('tipo_cliente') == 'INDIVIDUAL' else 1
                )
            
            with col2:
                activo = st.selectbox(
                    "Estado *",
                    ["SI", "NO"],
                    index=0 if datos_edicion.get('activo', 'SI') == 'SI' else 1
                )
                direccion = st.text_area(
                    "Dirección",
                    value=datos_edicion.get('direccion', ''),
                    placeholder="Av. Principal 123, Ciudad"
                )

            st.markdown("#### 📞 Información de Contacto")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                contacto_nombre = st.text_input(
                    "Nombre Contacto",
                    value=datos_edicion.get('contacto_nombre', ''),
                    placeholder="Juan Pérez"
                )
            with col2:
                contacto_telefono = st.text_input(
                    "Teléfono",
                    value=datos_edicion.get('contacto_telefono', ''),
                    placeholder="+503 2222-3333"
                )
            with col3:
                contacto_email = st.text_input(
                    "Email",
                    value=datos_edicion.get('contacto_email', ''),
                    placeholder="contacto@ejemplo.com"
                )

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button(
                    "💾 Guardar Cliente" if editando else "➕ Crear Cliente",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                cancelar = st.form_submit_button(
                    "❌ Cancelar",
                    use_container_width=True
                )

            if cancelar:
                st.session_state['editar_cliente_id'] = None
                st.session_state['editar_cliente_data'] = {}
                st.session_state['crear_cliente_activo'] = False
                st.rerun()

            if submitted:
                if not nombre or not nit:
                    st.error("❌ Por favor completa todos los campos obligatorios (*)")
                else:
                    try:
                        payload = {
                            "nombre": nombre,
                            "nit": nit,
                            "tipo_cliente": tipo_cliente,
                            "activo": activo,
                            "direccion": direccion if direccion else None,
                            "contacto_nombre": contacto_nombre if contacto_nombre else None,
                            "contacto_telefono": contacto_telefono if contacto_telefono else None,
                            "contacto_email": contacto_email if contacto_email else None
                        }

                        if editando:
                            # Actualizar cliente existente
                            resp = requests.put(
                                f"{backend_url}/api/clientes/{st.session_state['editar_cliente_id']}",
                                json=payload,
                                timeout=10
                            )
                            mensaje_exito = "✅ Cliente actualizado exitosamente"
                        else:
                            # Crear nuevo cliente
                            resp = requests.post(
                                f"{backend_url}/api/clientes/",
                                json=payload,
                                timeout=10
                            )
                            mensaje_exito = "✅ Cliente creado exitosamente"

                        if resp.status_code in [200, 201]:
                            cliente_guardado = resp.json()
                            st.success(f"{mensaje_exito}: {cliente_guardado['nombre']}")
                            st.balloons()
                            
                            # Limpiar estado
                            st.session_state['editar_cliente_id'] = None
                            st.session_state['editar_cliente_data'] = {}
                            st.session_state['crear_cliente_activo'] = False
                            
                            st.rerun()
                        else:
                            error_detail = resp.json().get('detail', resp.text)
                            st.error(f"❌ Error: {error_detail}")

                    except Exception as e:
                        st.error(f"❌ Error al guardar cliente: {str(e)}")

    # ============================
    # TAB 3: ESTADÍSTICAS
    # ============================
    with tab3:
        st.subheader("📊 Estadísticas de Clientes")
        
        try:
            resp_stats = requests.get(
                f"{backend_url}/api/clientes/estadisticas/resumen",
                timeout=10
            )
            resp_stats.raise_for_status()
            stats = resp_stats.json()

            # Mostrar métricas principales
            st.markdown("### 📈 Resumen General")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Clientes", stats.get('total_clientes', 0))
            with col2:
                st.metric("Activos", stats.get('clientes_activos', 0), delta="Activos")
            with col3:
                st.metric("Individuales", stats.get('clientes_individuales', 0))
            with col4:
                st.metric("Empresas", stats.get('clientes_empresas', 0))

            st.markdown("---")

            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔵 Distribución por Estado")
                df_estado = pd.DataFrame({
                    'Estado': ['Activos', 'Inactivos'],
                    'Cantidad': [
                        stats.get('clientes_activos', 0),
                        stats.get('total_clientes', 0) - stats.get('clientes_activos', 0)
                    ]
                })
                if df_estado['Cantidad'].sum() > 0:
                    st.bar_chart(df_estado.set_index('Estado'))
                else:
                    st.info("No hay datos para mostrar")
            
            with col2:
                st.markdown("### 🟢 Distribución por Tipo")
                df_tipo = pd.DataFrame({
                    'Tipo': ['Individuales', 'Empresas'],
                    'Cantidad': [
                        stats.get('clientes_individuales', 0),
                        stats.get('clientes_empresas', 0)
                    ]
                })
                if df_tipo['Cantidad'].sum() > 0:
                    st.bar_chart(df_tipo.set_index('Tipo'))
                else:
                    st.info("No hay datos para mostrar")

        except Exception as e:
            st.error(f"❌ Error obteniendo estadísticas: {e}")
