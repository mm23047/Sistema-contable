"""
Página Streamlit para gestionar Facturas.
Proporciona visualización completa y descarga de facturas con todos los datos fiscales.
"""
import streamlit as st
import requests
from datetime import datetime
import pandas as pd


def render_page(backend_url: str):
    st.title("📄 Sistema de Facturación")
    st.markdown("---")

    # ============================
    # Tabs para diferentes vistas
    # ============================
    tab1, tab2, tab3 = st.tabs(["📋 Listado de Facturas", "📊 Estadísticas", "➕ Crear Factura"])

    # ============================
    # TAB 1: LISTADO DE FACTURAS
    # ============================
    with tab1:
        st.subheader("Facturas Registradas")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_cliente = st.text_input("🔍 Filtrar por Cliente", "")
        with col2:
            filtro_nit = st.text_input("🔍 Filtrar por NIT", "")
        with col3:
            filtro_fecha = st.date_input("📅 Filtrar por Fecha", value=None)

        # Obtener facturas desde backend
        def get_facturas():
            try:
                params = {}
                if filtro_cliente:
                    params['cliente'] = filtro_cliente
                if filtro_nit:
                    params['nit_cliente'] = filtro_nit
                if filtro_fecha:
                    params['fecha_inicio'] = filtro_fecha.isoformat()
                    params['fecha_fin'] = filtro_fecha.isoformat()
                
                resp = requests.get(f"{backend_url}/api/facturas/", params=params, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                st.error(f"❌ Error obteniendo facturas: {e}")
                return []

        facturas = get_facturas()

        if not facturas:
            st.warning("📭 No hay facturas registradas aún.")
            st.info("💡 Las facturas se crean desde la pestaña **➕ Crear Factura** o automáticamente desde transacciones de INGRESO")
            return

        st.success(f"✅ Se encontraron {len(facturas)} factura(s)")
        st.markdown("---")

        # Mostrar facturas una por una con TODOS los detalles
        for fac in facturas:
            with st.expander(
                f"🧾 **{fac['numero_factura']}** - {fac['cliente']} - ${float(fac['monto_total']):,.2f}", 
                expanded=False
            ):
                # Sección 1: Información General
                st.markdown("### 📋 Información General")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Número de Factura", fac['numero_factura'])
                with col2:
                    fecha_emision = fac.get('fecha_emision', 'N/A')
                    if fecha_emision != 'N/A':
                        try:
                            fecha_obj = datetime.fromisoformat(fecha_emision.replace('Z', '+00:00'))
                            fecha_emision = fecha_obj.strftime('%d/%m/%Y')
                        except:
                            pass
                    st.metric("Fecha de Emisión", fecha_emision)
                with col3:
                    fecha_venc = fac.get('fecha_vencimiento', 'N/A')
                    if fecha_venc and fecha_venc != 'N/A':
                        try:
                            fecha_obj = datetime.fromisoformat(fecha_venc.replace('Z', '+00:00'))
                            fecha_venc = fecha_obj.strftime('%d/%m/%Y')
                        except:
                            pass
                    st.metric("Fecha de Vencimiento", fecha_venc if fecha_venc else 'N/A')
                with col4:
                    st.metric("ID Transacción", fac.get('id_transaccion', 'N/A'))

                st.markdown("---")

                # Sección 2: Datos del Cliente
                st.markdown("### 👤 Datos del Cliente")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Cliente:** {fac['cliente']}")
                    st.write(f"**NIT:** {fac.get('nit_cliente', 'N/A')}")
                    st.write(f"**Teléfono:** {fac.get('telefono_cliente', 'N/A')}")
                with col2:
                    st.write(f"**Email:** {fac.get('email_cliente', 'N/A')}")
                    st.write(f"**Dirección:** {fac.get('direccion_cliente', 'N/A')}")

                st.markdown("---")

                # Sección 2.5: Producto/Servicio
                st.markdown("### 📦 Producto o Servicio")
                st.info(fac.get('producto_servicio', 'No especificado'))

                st.markdown("---")

                # Sección 3: Detalles Financieros
                st.markdown("### 💰 Detalles Financieros")
                col1, col2, col3, col4 = st.columns(4)
                
                subtotal = float(fac.get('subtotal', 0))
                descuento = float(fac.get('descuento', 0))
                iva = float(fac.get('iva', 0))
                total = float(fac.get('monto_total', 0))
                
                with col1:
                    st.metric("Subtotal", f"${subtotal:,.2f}")
                with col2:
                    st.metric("Descuento", f"${descuento:,.2f}", delta=f"-{descuento:,.2f}" if descuento > 0 else None)
                with col3:
                    st.metric("IVA (13%)", f"${iva:,.2f}")
                with col4:
                    st.metric("TOTAL", f"${total:,.2f}", delta="Final")

                st.markdown("---")

                # Sección 4: Información Adicional
                st.markdown("### 📝 Información Adicional")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Vendedor:** {fac.get('vendedor', 'N/A')}")
                    st.write(f"**Condiciones de Pago:** {fac.get('condiciones_pago', 'N/A')}")
                with col2:
                    notas = fac.get('notas', 'Sin notas')
                    st.write(f"**Notas:**")
                    st.info(notas if notas else "Sin notas adicionales")

                st.markdown("---")

                # Botones de descarga
                st.markdown("### 📥 Descargar Factura")
                col1, col2, col3 = st.columns(3)

                # PDF
                with col1:
                    if st.button(
                            "📄 Descargar PDF",
                            key=f"pdf_{fac['id_factura']}",
                            use_container_width=True,
                            type="primary"
                    ):
                        try:
                            pdf_response = requests.get(
                                f"{backend_url}/api/facturas/{fac['id_factura']}/descargar-pdf",
                                timeout=30
                            )

                            if pdf_response.status_code == 200:
                                st.download_button(
                                    label="⬇️ Clic aquí para descargar PDF",
                                    data=pdf_response.content,
                                    file_name=f"factura_{fac['numero_factura']}.pdf",
                                    mime="application/pdf",
                                    key=f"btn_pdf_{fac['id_factura']}",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Error generando PDF: {pdf_response.status_code}")
                        except Exception as e:
                            st.error(f"❌ Error al descargar PDF: {str(e)}")

                # EXCEL
                with col2:
                    if st.button(
                            "📊 Descargar Excel",
                            key=f"excel_{fac['id_factura']}",
                            use_container_width=True,
                            type="secondary"
                    ):
                        try:
                            excel_response = requests.get(
                                f"{backend_url}/api/facturas/{fac['id_factura']}/descargar-excel",
                                timeout=30
                            )

                            if excel_response.status_code == 200:
                                st.download_button(
                                    label="⬇️ Clic aquí para descargar Excel",
                                    data=excel_response.content,
                                    file_name=f"factura_{fac['numero_factura']}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"btn_excel_{fac['id_factura']}",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Error generando Excel: {excel_response.status_code}")
                        except Exception as e:
                            st.error(f"❌ Error al descargar Excel: {str(e)}")

                # JSON
                with col3:
                    if st.button(
                            "📋 Descargar JSON",
                            key=f"json_{fac['id_factura']}",
                            use_container_width=True,
                            type="secondary"
                    ):
                        try:
                            json_response = requests.get(
                                f"{backend_url}/api/facturas/{fac['id_factura']}/descargar-json",
                                timeout=30
                            )

                            if json_response.status_code == 200:
                                st.download_button(
                                    label="⬇️ Clic aquí para descargar JSON",
                                    data=json_response.content,
                                    file_name=f"factura_{fac['numero_factura']}.json",
                                    mime="application/json",
                                    key=f"btn_json_{fac['id_factura']}",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Error generando JSON: {json_response.status_code}")
                        except Exception as e:
                            st.error(f"❌ Error al descargar JSON: {str(e)}")

    # ============================
    # TAB 2: ESTADÍSTICAS
    # ============================
    with tab2:
        st.subheader("📊 Estadísticas de Facturación")
        
        # Filtros de fecha para estadísticas
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio_stats = st.date_input("📅 Fecha Inicio", value=None, key="stats_inicio")
        with col2:
            fecha_fin_stats = st.date_input("📅 Fecha Fin", value=None, key="stats_fin")

        # Obtener estadísticas
        try:
            params_stats = {}
            if fecha_inicio_stats:
                params_stats['fecha_inicio'] = fecha_inicio_stats.isoformat()
            if fecha_fin_stats:
                params_stats['fecha_fin'] = fecha_fin_stats.isoformat()
            
            resp_stats = requests.get(
                f"{backend_url}/api/facturas/estadisticas/resumen",
                params=params_stats,
                timeout=10
            )
            resp_stats.raise_for_status()
            stats = resp_stats.json()

            # Mostrar métricas
            st.markdown("### 💵 Resumen Financiero")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Facturas", stats.get('total_facturas', 0))
            with col2:
                st.metric("Monto Total", f"${float(stats.get('monto_total', 0)):,.2f}")
            with col3:
                st.metric("IVA Recaudado", f"${float(stats.get('total_iva', 0)):,.2f}")
            with col4:
                st.metric("Descuentos", f"${float(stats.get('total_descuentos', 0)):,.2f}")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Promedio por Venta", f"${float(stats.get('promedio_venta', 0)):,.2f}")

        except Exception as e:
            st.error(f"❌ Error obteniendo estadísticas: {e}")

        st.markdown("---")

        # Top Clientes
        st.markdown("### 🏆 Top Clientes")
        try:
            top_n = st.slider("Mostrar top:", 5, 20, 10)
            resp_top = requests.get(
                f"{backend_url}/api/facturas/estadisticas/top-clientes",
                params={'top': top_n},
                timeout=10
            )
            resp_top.raise_for_status()
            top_clientes = resp_top.json()

            if top_clientes:
                df_top = pd.DataFrame(top_clientes)
                df_top['total_compras'] = df_top['total_compras'].apply(lambda x: f"${float(x):,.2f}")
                df_top.columns = ['Cliente', 'NIT', 'Total Compras', 'Cantidad Facturas']
                st.dataframe(df_top, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de clientes disponibles")

        except Exception as e:
            st.error(f"❌ Error obteniendo top clientes: {e}")

    # ============================
    # TAB 3: CREAR FACTURA
    # ============================
    with tab3:
        st.subheader("➕ Crear Nueva Factura")
        st.info("💡 **Nota:** Selecciona cliente y productos del catálogo. Los asientos contables se crean manualmente.")

        # Obtener clientes activos
        def get_clientes_activos():
            try:
                resp = requests.get(f"{backend_url}/api/clientes/", params={'activo': 'SI'}, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                st.error(f"❌ Error obteniendo clientes: {e}")
                return []

        # Obtener productos activos
        def get_productos_activos():
            try:
                resp = requests.get(f"{backend_url}/api/productos/", params={'activo': 'SI'}, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                st.error(f"❌ Error obteniendo productos: {e}")
                return []

        clientes_disponibles = get_clientes_activos()
        productos_disponibles = get_productos_activos()

        if not clientes_disponibles:
            st.warning("⚠️ No hay clientes registrados. Crea uno desde el módulo de Clientes.")
            return

        if not productos_disponibles:
            st.warning("⚠️ No hay productos registrados. Crea uno desde el módulo de Productos.")
            return

        # Inicializar líneas de productos en session_state
        if 'lineas_factura' not in st.session_state:
            st.session_state.lineas_factura = []

        # ====== SECCIÓN 1: SELECCIÓN DE CLIENTE ======
        st.markdown("#### 1️⃣ Selección de Cliente")
        
        # Crear diccionario de clientes
        clientes_dict = {f"{c['nombre']} - {c['nit']}": c for c in clientes_disponibles}
        cliente_seleccionado_str = st.selectbox(
            "Cliente *",
            options=list(clientes_dict.keys()),
            key="cliente_select_main"
        )
        cliente_seleccionado = clientes_dict[cliente_seleccionado_str]
        
        # Mostrar info del cliente
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📧 {cliente_seleccionado.get('email', 'N/A')}")
        with col2:
            st.info(f"📱 {cliente_seleccionado.get('telefono', 'N/A')}")
        with col3:
            st.info(f"🏢 {cliente_seleccionado.get('tipo_cliente', 'N/A')}")

        st.markdown("---")

        # ====== SECCIÓN 2: AGREGAR PRODUCTOS (FUERA DEL FORM) ======
        st.markdown("#### 2️⃣ Agregar Productos/Servicios")
        
        # Crear diccionario de productos
        productos_dict = {f"{p['codigo']} - {p['nombre']} (${float(p['precio_unitario']):.2f})": p for p in productos_disponibles}

        st.markdown("**Selecciona un producto:**")
        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
        with col1:
            producto_agregar_key = st.selectbox(
                "Producto",
                options=list(productos_dict.keys()),
                key="producto_select_main"
            )
        with col2:
            cantidad_agregar = st.number_input(
                "Cantidad",
                min_value=0.01,
                step=1.0,
                value=1.0,
                key="cantidad_input_main"
            )
        with col3:
            descuento_pct = st.number_input(
                "Desc %",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                value=0.0,
                key="descuento_input_main"
            )
        with col4:
            if st.button("➕ Agregar a Factura", use_container_width=True, type="primary"):
                if producto_agregar_key in productos_dict:
                    producto_sel = productos_dict[producto_agregar_key]
                    st.session_state.lineas_factura.append({
                        'id_producto': producto_sel['id_producto'],
                        'codigo': producto_sel['codigo'],
                        'nombre': producto_sel['nombre'],
                        'cantidad': cantidad_agregar,
                        'precio_unitario': float(producto_sel['precio_unitario']),
                        'descuento_porcentaje': descuento_pct,
                        'aplica_iva': producto_sel['aplica_iva']
                    })
                    st.success(f"✅ Producto agregado: {producto_sel['nombre']}")
                    st.rerun()

        st.markdown("---")
        # ====== SECCIÓN 3: MOSTRAR LÍNEAS AGREGADAS ======
        if st.session_state.lineas_factura:
            st.markdown("**📝 Productos en la Factura:**")
            
            # Calcular totales por línea
            lineas_display = []
            subtotal_general = 0.0
            iva_general = 0.0
            
            for idx, linea in enumerate(st.session_state.lineas_factura):
                subtotal_linea = linea['cantidad'] * linea['precio_unitario']
                desc_linea = subtotal_linea * (linea['descuento_porcentaje'] / 100)
                subtotal_linea_neto = subtotal_linea - desc_linea
                
                if linea['aplica_iva'] == 'SI':
                    iva_linea = subtotal_linea_neto * 0.13
                else:
                    iva_linea = 0.0
                
                total_linea = subtotal_linea_neto + iva_linea
                
                subtotal_general += subtotal_linea_neto
                iva_general += iva_linea
                
                lineas_display.append({
                    '#': idx + 1,
                    'Código': linea['codigo'],
                    'Producto': linea['nombre'],
                    'Cant': linea['cantidad'],
                    'Precio': f"${linea['precio_unitario']:.2f}",
                    'Desc %': f"{linea['descuento_porcentaje']:.1f}%",
                    'Subtotal': f"${subtotal_linea_neto:.2f}",
                    'IVA': f"${iva_linea:.2f}",
                    'Total': f"${total_linea:.2f}"
                })
            
            df_lineas = pd.DataFrame(lineas_display)
            st.dataframe(df_lineas, use_container_width=True, hide_index=True)
            
            # Botón para limpiar líneas
            if st.button("🗑️ Limpiar Todos los Productos", type="secondary"):
                st.session_state.lineas_factura = []
                st.rerun()
        else:
            st.info("📝 Agrega productos usando el selector de arriba")

        st.markdown("---")

        # ====== FORMULARIO FINAL PARA CREAR FACTURA ======
        with st.form("crear_factura_form"):
            st.markdown("#### 3️⃣ Información Adicional y Totales")
            
            # Descuento global y totales
            col1, col2 = st.columns(2)
            with col1:
                descuento_global = st.number_input(
                    "Descuento Global Adicional ($)",
                    min_value=0.0,
                    step=0.01,
                    value=0.0,
                    format="%.2f",
                    key="descuento_global_input"
                )
            
            # Calcular totales finales
            if st.session_state.lineas_factura:
                monto_total_final = subtotal_general + iva_general - descuento_global
                
                with col2:
                    st.markdown("**Totales:**")
                    st.write(f"Subtotal: ${subtotal_general:.2f}")
                    st.write(f"IVA: ${iva_general:.2f}")
                    st.write(f"Descuento Global: ${descuento_global:.2f}")
                    st.write(f"**💰 TOTAL: ${monto_total_final:.2f}**")

            st.markdown("---")
            st.markdown("#### 4️⃣ Datos Adicionales")
            
            col1, col2 = st.columns(2)
            with col1:
                vendedor = st.text_input("Vendedor", placeholder="Juan Pérez", key="vendedor_input")
                condiciones = st.selectbox("Condiciones de Pago", ["Contado", "Crédito"], key="condiciones_input")
            with col2:
                fecha_vencimiento = st.date_input("Fecha de Vencimiento", value=None, key="fecha_venc_input")
                notas = st.text_area("Notas", placeholder="Información adicional...", key="notas_input")

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ Crear Factura Completa", use_container_width=True, type="primary")

            if submitted:
                if not st.session_state.lineas_factura:
                    st.error("❌ Debes agregar al menos un producto a la factura")
                else:
                    try:
                        # Preparar detalles para el backend
                        detalles = [
                            {
                                "id_producto": linea['id_producto'],
                                "cantidad": linea['cantidad'],
                                "precio_unitario": linea['precio_unitario'],
                                "descuento_porcentaje": linea['descuento_porcentaje'],
                                "descuento_monto": 0
                            }
                            for linea in st.session_state.lineas_factura
                        ]

                        payload = {
                            "id_cliente": cliente_seleccionado['id_cliente'],
                            "condiciones_pago": condiciones,
                            "vendedor": vendedor if vendedor else None,
                            "notas": notas if notas else None,
                            "fecha_vencimiento": fecha_vencimiento.isoformat() if fecha_vencimiento else None,
                            "descuento_global": descuento_global,
                            "detalles": detalles
                        }

                        resp_create = requests.post(
                            f"{backend_url}/api/facturas/con-detalles",
                            json=payload,
                            timeout=10
                        )

                        if resp_create.status_code == 201:
                            factura_creada = resp_create.json()
                            st.success(f"✅ Factura creada exitosamente: {factura_creada['numero_factura']}")
                            st.success(f"💵 Monto Total: ${float(factura_creada['monto_total']):.2f}")
                            st.balloons()
                            
                            # Limpiar líneas
                            st.session_state.lineas_factura = []
                            st.rerun()
                        else:
                            error_detail = resp_create.json().get('detail', resp_create.text)
                            st.error(f"❌ Error creando factura: {error_detail}")

                    except Exception as e:
                        st.error(f"❌ Error al crear factura: {str(e)}")