"""
Página Streamlit para gestionar Facturas.
Proporciona visualización y descarga de facturas generadas automáticamente.
"""
import streamlit as st
import requests


def render_page(backend_url: str):
    st.title("📄 Facturas Registradas")
    st.markdown("---")

    # ============================
    # Obtener facturas desde backend
    # ============================
    def get_facturas():
        try:
            resp = requests.get(f"{backend_url}/api/facturas/", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            st.error(f"❌ Error obteniendo facturas: {e}")
            return []

    facturas = get_facturas()

    if not facturas:
        st.warning("📭 No hay facturas registradas aún.")
        st.info("💡 Las facturas se generan automáticamente cuando creas una transacción de tipo **VENTA**")
        return

    st.success(f"✅ Se encontraron {len(facturas)} factura(s)")
    st.markdown("---")

    # ============================
    # Mostrar facturas una por una
    # ============================
    for fac in facturas:
        with st.expander(f"🧾 Factura #{fac['numero_factura']} - Cliente: {fac['cliente']}", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("ID Factura", fac['id_factura'])
                st.metric("Número", f"#{fac['numero_factura']}")

            with col2:
                st.metric("Cliente", fac['cliente'])
                st.metric("Monto Total", f"${float(fac['monto_total']):,.2f}")

            with col3:
                st.metric("Transacción", fac['id_transaccion'])
                st.metric("Estado", "✅ Generada")

            st.write(f"**Fecha de Emisión:** {fac['fecha_emision']}")

            st.markdown("---")

            # ============================
            # Botones de descarga
            # ============================
            col1, col2 = st.columns(2)

            # PDF
            with col1:
                if st.button(
                        "📥 Descargar PDF",
                        key=f"pdf_{fac['id_factura']}",
                        use_container_width=True
                ):
                    try:
                        pdf_response = requests.get(
                            f"{backend_url}/api/facturas/{fac['id_factura']}/descargar-pdf",
                            timeout=30
                        )

                        if pdf_response.status_code == 200:
                            st.download_button(
                                label="⬇️ Clic aquí para descargar",
                                data=pdf_response.content,
                                file_name=f"Factura_{fac['numero_factura']}.pdf",
                                mime="application/pdf",
                                key=f"btn_pdf_{fac['id_factura']}"
                            )
                        else:
                            st.error(f"❌ Error generando PDF: {pdf_response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Error al descargar PDF: {str(e)}")

            # EXCEL
            with col2:
                if st.button(
                        "📥 Descargar Excel",
                        key=f"excel_{fac['id_factura']}",
                        use_container_width=True
                ):
                    try:
                        excel_response = requests.get(
                            f"{backend_url}/api/facturas/{fac['id_factura']}/descargar-excel",
                            timeout=30
                        )

                        if excel_response.status_code == 200:
                            st.download_button(
                                label="⬇️ Clic aquí para descargar",
                                data=excel_response.content,
                                file_name=f"Factura_{fac['numero_factura']}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"btn_excel_{fac['id_factura']}"
                            )
                        else:
                            st.error(f"❌ Error generando Excel: {excel_response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Error al descargar Excel: {str(e)}")

            st.markdown("---")