"""
Página Streamlit para gestionar Productos y Servicios.
Proporciona CRUD completo con control de inventario y alertas de stock.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from decimal import Decimal


def render_page(backend_url: str):
    """Renderizar la página de gestión de productos"""
    st.title("📦 Gestión de Productos y Servicios")
    st.markdown("---")

    # ============================
    # Tabs para diferentes vistas
    # ============================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Catálogo", 
        "➕ Crear/Editar", 
        "⚠️ Alertas de Stock",
        "📊 Estadísticas"
    ])

    # ============================
    # TAB 1: CATÁLOGO DE PRODUCTOS
    # ============================
    with tab1:
        st.subheader("Catálogo de Productos y Servicios")
        
        # Filtros de búsqueda
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            busqueda = st.text_input("🔍 Buscar", placeholder="Nombre, código o descripción...")
        with col2:
            tipo_filtro = st.selectbox("Tipo", ["Todos", "PRODUCTO", "SERVICIO"])
        with col3:
            activo_filtro = st.selectbox("Estado", ["Todos", "SI", "NO"])
        with col4:
            bajo_stock = st.checkbox("Solo bajo stock")

        # Botones de acción
        col_refresh, col_new = st.columns([3, 1])
        with col_refresh:
            if st.button("🔄 Actualizar Catálogo", use_container_width=True):
                st.rerun()
        with col_new:
            if st.button("➕ Nuevo Producto", use_container_width=True, type="primary"):
                st.session_state['crear_producto_activo'] = True
                st.session_state['editar_producto_id'] = None
                st.rerun()

        # Obtener productos desde backend
        def get_productos():
            try:
                params = {}
                if busqueda:
                    params['busqueda'] = busqueda
                if tipo_filtro != "Todos":
                    params['tipo'] = tipo_filtro
                if activo_filtro != "Todos":
                    params['activo'] = activo_filtro
                if bajo_stock:
                    params['bajo_stock'] = True
                
                resp = requests.get(f"{backend_url}/api/productos/", params=params, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                st.error(f"❌ Error obteniendo productos: {e}")
                return []

        productos = get_productos()

        if not productos:
            st.warning("📭 No hay productos registrados aún.")
            st.info("💡 Crea tu primer producto desde la pestaña **➕ Crear/Editar**")
        else:
            st.success(f"✅ Se encontraron {len(productos)} producto(s)/servicio(s)")
            st.markdown("---")

            # Mostrar productos
            for producto in productos:
                # Color según tipo
                icono = "📦" if producto['tipo'] == 'PRODUCTO' else "🔧"
                
                # Alerta de stock bajo
                stock_bajo = False
                if producto['tipo'] == 'PRODUCTO':
                    stock_actual = float(producto.get('stock_actual', 0))
                    stock_minimo = float(producto.get('stock_minimo', 0))
                    stock_bajo = stock_actual < stock_minimo
                
                titulo = f"{icono} **{producto['codigo']}** - {producto['nombre']}"
                if stock_bajo:
                    titulo = f"⚠️ {titulo} - **STOCK BAJO**"

                with st.expander(titulo, expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {producto['id_producto']}")
                        st.write(f"**Código SKU:** {producto['codigo']}")
                        st.write(f"**Nombre:** {producto['nombre']}")
                        st.write(f"**Tipo:** {producto['tipo']}")
                        st.write(f"**Categoría:** {producto.get('categoria', 'N/A')}")
                        st.write(f"**Descripción:** {producto.get('descripcion', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Precio Unitario:** ${float(producto['precio_unitario']):,.2f}")
                        st.write(f"**Precio Costo:** ${float(producto.get('precio_costo', 0)):,.2f}")
                        st.write(f"**Aplica IVA:** {'✅ Sí' if producto['aplica_iva'] == 'SI' else '❌ No'}")
                        
                        if producto['tipo'] == 'PRODUCTO':
                            stock_color = "🔴" if stock_bajo else "🟢"
                            st.write(f"**Stock Actual:** {stock_color} {float(producto.get('stock_actual', 0)):.0f}")
                            st.write(f"**Stock Mínimo:** {float(producto.get('stock_minimo', 0)):.0f}")
                        else:
                            st.write("**Stock:** N/A (Servicio)")
                        
                        st.write(f"**Activo:** {'✅ Sí' if producto['activo'] == 'SI' else '❌ No'}")

                    st.markdown("---")
                    
                    # Botones de acción
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(
                            "✏️ Editar", 
                            key=f"edit_prod_{producto['id_producto']}", 
                            use_container_width=True
                        ):
                            st.session_state['editar_producto_id'] = producto['id_producto']
                            st.session_state['editar_producto_data'] = producto
                            st.session_state['crear_producto_activo'] = False
                            st.rerun()
                    
                    with col2:
                        if producto['tipo'] == 'PRODUCTO':
                            if st.button(
                                "📊 Ajustar Stock", 
                                key=f"stock_{producto['id_producto']}", 
                                use_container_width=True
                            ):
                                st.session_state['ajustar_stock_id'] = producto['id_producto']
                                st.session_state['ajustar_stock_nombre'] = producto['nombre']
                                st.session_state['ajustar_stock_actual'] = float(producto.get('stock_actual', 0))
                    
                    with col3:
                        if producto['activo'] == 'SI':
                            if st.button(
                                "🚫 Desactivar", 
                                key=f"deact_prod_{producto['id_producto']}", 
                                use_container_width=True
                            ):
                                try:
                                    resp = requests.patch(
                                        f"{backend_url}/api/productos/{producto['id_producto']}/desactivar",
                                        timeout=10
                                    )
                                    if resp.status_code == 200:
                                        st.success("✅ Producto desactivado")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Error: {resp.text}")
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                    
                    with col4:
                        if st.button(
                            "💰 Ver Precio+IVA", 
                            key=f"iva_{producto['id_producto']}", 
                            use_container_width=True
                        ):
                            try:
                                resp = requests.get(
                                    f"{backend_url}/api/productos/{producto['id_producto']}/precio-iva",
                                    timeout=10
                                )
                                if resp.status_code == 200:
                                    data = resp.json()
                                    st.info(f"💵 Precio con IVA: ${float(data['precio_con_iva']):,.2f}")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

        # Modal de ajuste de stock
        if st.session_state.get('ajustar_stock_id'):
            st.markdown("---")
            st.subheader(f"📊 Ajustar Stock: {st.session_state.get('ajustar_stock_nombre')}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Stock Actual", f"{st.session_state.get('ajustar_stock_actual', 0):.0f}")
            
            with col2:
                tipo_ajuste = st.radio(
                    "Tipo de Ajuste",
                    ["➕ Entrada (Compra)", "➖ Salida (Venta)"],
                    horizontal=True
                )
            
            cantidad_ajuste = st.number_input(
                "Cantidad a Ajustar",
                min_value=0.01,
                step=1.0,
                format="%.2f"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Aplicar Ajuste", use_container_width=True, type="primary"):
                    try:
                        # Positivo para entrada, negativo para salida
                        cantidad_final = cantidad_ajuste if "Entrada" in tipo_ajuste else -cantidad_ajuste
                        
                        resp = requests.patch(
                            f"{backend_url}/api/productos/{st.session_state['ajustar_stock_id']}/stock",
                            params={'cantidad': cantidad_final},
                            timeout=10
                        )
                        
                        if resp.status_code == 200:
                            producto_actualizado = resp.json()
                            nuevo_stock = float(producto_actualizado['stock_actual'])
                            st.success(f"✅ Stock actualizado: {nuevo_stock:.0f} unidades")
                            
                            # Limpiar estado
                            del st.session_state['ajustar_stock_id']
                            del st.session_state['ajustar_stock_nombre']
                            del st.session_state['ajustar_stock_actual']
                            
                            st.rerun()
                        else:
                            error_detail = resp.json().get('detail', resp.text)
                            st.error(f"❌ Error: {error_detail}")
                    except Exception as e:
                        st.error(f"❌ Error al ajustar stock: {e}")
            
            with col2:
                if st.button("❌ Cancelar", use_container_width=True):
                    del st.session_state['ajustar_stock_id']
                    del st.session_state['ajustar_stock_nombre']
                    del st.session_state['ajustar_stock_actual']
                    st.rerun()

    # ============================
    # TAB 2: CREAR/EDITAR PRODUCTO
    # ============================
    with tab2:
        editando = st.session_state.get('editar_producto_id') is not None
        datos_edicion = st.session_state.get('editar_producto_data', {})

        if editando:
            st.subheader(f"✏️ Editar: {datos_edicion.get('nombre', '')}")
        else:
            st.subheader("➕ Crear Nuevo Producto/Servicio")

        with st.form("form_producto"):
            st.markdown("#### 📋 Información Básica")
            col1, col2 = st.columns(2)
            
            with col1:
                codigo = st.text_input(
                    "Código SKU *",
                    value=datos_edicion.get('codigo', ''),
                    placeholder="LAP-HP-001"
                )
                nombre = st.text_input(
                    "Nombre del Producto/Servicio *",
                    value=datos_edicion.get('nombre', ''),
                    placeholder="Laptop HP ProBook 450 G8"
                )
                tipo = st.selectbox(
                    "Tipo *",
                    ["PRODUCTO", "SERVICIO"],
                    index=0 if datos_edicion.get('tipo') == 'PRODUCTO' else 1
                )
            
            with col2:
                categoria = st.text_input(
                    "Categoría",
                    value=datos_edicion.get('categoria', ''),
                    placeholder="Equipos de Cómputo"
                )
                descripcion = st.text_area(
                    "Descripción",
                    value=datos_edicion.get('descripcion', ''),
                    placeholder="Intel i5, 8GB RAM, 256GB SSD"
                )
                activo = st.selectbox(
                    "Estado *",
                    ["SI", "NO"],
                    index=0 if datos_edicion.get('activo', 'SI') == 'SI' else 1
                )

            st.markdown("#### 💰 Precios")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                precio_unitario = st.number_input(
                    "Precio Unitario *",
                    min_value=0.01,
                    step=0.01,
                    value=max(0.01, float(datos_edicion.get('precio_unitario', 0.01))),
                    format="%.2f"
                )
            with col2:
                precio_costo = st.number_input(
                    "Precio Costo",
                    min_value=0.0,
                    step=0.01,
                    value=float(datos_edicion.get('precio_costo', 0.0)),
                    format="%.2f"
                )
            with col3:
                aplica_iva = st.selectbox(
                    "Aplica IVA *",
                    ["SI", "NO"],
                    index=0 if datos_edicion.get('aplica_iva', 'SI') == 'SI' else 1
                )

            # Mostrar campos de stock solo para PRODUCTOS
            tipo_seleccionado = tipo if not editando else datos_edicion.get('tipo', 'PRODUCTO')
            
            if tipo_seleccionado == 'PRODUCTO':
                st.markdown("#### 📊 Inventario")
                col1, col2 = st.columns(2)
                
                with col1:
                    stock_actual = st.number_input(
                        "Stock Actual",
                        min_value=0.0,
                        step=1.0,
                        value=float(datos_edicion.get('stock_actual', 0.0)),
                        format="%.2f"
                    )
                with col2:
                    stock_minimo = st.number_input(
                        "Stock Mínimo (Alerta)",
                        min_value=0.0,
                        step=1.0,
                        value=float(datos_edicion.get('stock_minimo', 0.0)),
                        format="%.2f"
                    )
            else:
                stock_actual = 0
                stock_minimo = 0
                st.info("ℹ️ Los servicios no manejan inventario")

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button(
                    "💾 Guardar" if editando else "➕ Crear Producto",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                cancelar = st.form_submit_button(
                    "❌ Cancelar",
                    use_container_width=True
                )

            if cancelar:
                st.session_state['editar_producto_id'] = None
                st.session_state['editar_producto_data'] = {}
                st.session_state['crear_producto_activo'] = False
                st.rerun()

            if submitted:
                if not codigo or not nombre or precio_unitario <= 0:
                    st.error("❌ Por favor completa todos los campos obligatorios (*)")
                else:
                    try:
                        payload = {
                            "codigo": codigo,
                            "nombre": nombre,
                            "tipo": tipo,
                            "categoria": categoria if categoria else None,
                            "descripcion": descripcion if descripcion else None,
                            "precio_unitario": precio_unitario,
                            "precio_costo": precio_costo,
                            "aplica_iva": aplica_iva,
                            "activo": activo,
                            "stock_actual": stock_actual,
                            "stock_minimo": stock_minimo
                        }

                        if editando:
                            resp = requests.put(
                                f"{backend_url}/api/productos/{st.session_state['editar_producto_id']}",
                                json=payload,
                                timeout=10
                            )
                            mensaje_exito = "✅ Producto actualizado exitosamente"
                        else:
                            resp = requests.post(
                                f"{backend_url}/api/productos/",
                                json=payload,
                                timeout=10
                            )
                            mensaje_exito = "✅ Producto creado exitosamente"

                        if resp.status_code in [200, 201]:
                            producto_guardado = resp.json()
                            st.success(f"{mensaje_exito}: {producto_guardado['nombre']}")
                            st.balloons()
                            
                            # Limpiar estado
                            st.session_state['editar_producto_id'] = None
                            st.session_state['editar_producto_data'] = {}
                            st.session_state['crear_producto_activo'] = False
                            
                            st.rerun()
                        else:
                            error_detail = resp.json().get('detail', resp.text)
                            st.error(f"❌ Error: {error_detail}")

                    except Exception as e:
                        st.error(f"❌ Error al guardar producto: {str(e)}")

    # ============================
    # TAB 3: ALERTAS DE STOCK
    # ============================
    with tab3:
        st.subheader("⚠️ Productos con Stock Bajo")
        
        try:
            resp = requests.get(f"{backend_url}/api/productos/alertas/bajo-stock", timeout=10)
            resp.raise_for_status()
            productos_bajo_stock = resp.json()

            if not productos_bajo_stock:
                st.success("✅ No hay productos con stock bajo. ¡Todo en orden!")
            else:
                st.warning(f"⚠️ {len(productos_bajo_stock)} producto(s) requieren reabastecimiento")
                
                for producto in productos_bajo_stock:
                    stock_actual = float(producto.get('stock_actual', 0))
                    stock_minimo = float(producto.get('stock_minimo', 0))
                    diferencia = stock_minimo - stock_actual
                    
                    with st.expander(
                        f"🔴 {producto['codigo']} - {producto['nombre']} (Stock: {stock_actual:.0f} / Mínimo: {stock_minimo:.0f})",
                        expanded=True
                    ):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Stock Actual", f"{stock_actual:.0f}", delta=f"-{diferencia:.0f}", delta_color="inverse")
                        with col2:
                            st.metric("Stock Mínimo", f"{stock_minimo:.0f}")
                        with col3:
                            st.metric("Faltante", f"{diferencia:.0f}", delta_color="off")
                        
                        st.write(f"**Precio Unitario:** ${float(producto['precio_unitario']):,.2f}")
                        st.write(f"**Costo de Reabastecimiento:** ${(diferencia * float(producto.get('precio_costo', 0))):,.2f}")

        except Exception as e:
            st.error(f"❌ Error obteniendo alertas: {e}")

    # ============================
    # TAB 4: ESTADÍSTICAS
    # ============================
    with tab4:
        st.subheader("📊 Estadísticas del Catálogo")
        
        try:
            resp_stats = requests.get(
                f"{backend_url}/api/productos/estadisticas/resumen",
                timeout=10
            )
            resp_stats.raise_for_status()
            stats = resp_stats.json()

            st.markdown("### 📈 Resumen General")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Items", stats.get('total_productos', 0))
            with col2:
                st.metric("Productos", stats.get('total_productos_fisicos', 0))
            with col3:
                st.metric("Servicios", stats.get('total_servicios', 0))
            with col4:
                st.metric("Activos", stats.get('productos_activos', 0))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valor Inventario", f"${float(stats.get('valor_total_inventario', 0)):,.2f}")
            with col2:
                st.metric("Bajo Stock", stats.get('productos_bajo_stock', 0), delta="Alerta" if stats.get('productos_bajo_stock', 0) > 0 else None)
            with col3:
                promedio = stats.get('precio_promedio', 0)
                st.metric("Precio Promedio", f"${float(promedio):,.2f}")

        except Exception as e:
            st.error(f"❌ Error obteniendo estadísticas: {e}")
