"""
Página Streamlit para el Libro Mayor.
Diseño: tabs -> Resumen / Subcuentas / Exportar
Consumir endpoint backend: /api/libro_mayor
"""

import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from typing import Optional, List, Dict

def render_page(backend_url: str):
    """Renderizar la página de Libro Mayor"""
    st.header("📘 Libro Mayor")

    # Tabs para la página de Libro Mayor
    tab_resumen, tab_subcuentas, tab_exportar = st.tabs(["📘 Resumen por Cuentas Mayores", "📄 Subcuentas Detalladas", "📤 Exportar Libro Mayor"])

    with tab_resumen:
        mostrar_resumen(backend_url)

    with tab_subcuentas:
        mostrar_subcuentas(backend_url)

    with tab_exportar:
        exportar_libro_mayor(backend_url)


def _consultar_api_libro_mayor(backend_url: str, digitos: int, fecha_inicio: Optional[str], fecha_fin: Optional[str], incluir_detalle: bool, timeout: int = 30):
    """Helper que consulta el endpoint /api/libro_mayor y devuelve la lista de mayores"""
    params = {"digitos": digitos, "incluir_detalle": str(incluir_detalle).lower()}
    if fecha_inicio:
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        params["fecha_fin"] = fecha_fin

    try:
        resp = requests.get(f"{backend_url}/api/libro_mayor", params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        
        # Validar estructura de respuesta
        if not isinstance(data, dict) or "mayores" not in data:
            st.error("❌ Respuesta del servidor inválida")
            return None
            
        return data.get("mayores", [])
    except requests.exceptions.Timeout:
        st.error("⏱️ Tiempo de espera agotado. El servidor tardó demasiado en responder.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Error de conexión. Verifica que el backend esté ejecutándose.")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            try:
                error_detail = e.response.json().get("detail", "Error de validación")
                st.error(f"❌ Error de validación: {error_detail}")
            except:
                st.error("❌ Error de validación en los parámetros")
        else:
            st.error(f"❌ Error del servidor: {e.response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error inesperado: {e}")
        return None


def mostrar_resumen(backend_url: str):
    """Tab: Resumen por cuentas mayores"""
    st.subheader("Resumen por cuentas mayores")

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        digitos = st.number_input("Dígitos para cuenta mayor", min_value=1, max_value=10, value=4)
    with col2:
        fecha_inicio = st.date_input("Fecha inicio", value=None)
    with col3:
        fecha_fin = st.date_input("Fecha fin", value=None)

    incluir_detalle = st.checkbox("Incluir subcuentas (en detalle)", value=False)

    if st.button("🔍 Cargar Libro Mayor", type="primary"):
        # convertir fechas a iso si existen
        fi = fecha_inicio.isoformat() if fecha_inicio else None
        ff = fecha_fin.isoformat() if fecha_fin else None

        mayores = _consultar_api_libro_mayor(backend_url, digitos, fi, ff, incluir_detalle)
        if mayores is None:
            return

        if not mayores:
            st.info("📭 No se encontraron cuentas para los filtros seleccionados.")
            return

        # DataFrame resumen
        df = pd.DataFrame([{
            "codigo_mayor": m["codigo_mayor"],
            "nombre_mayor": m["nombre_mayor"],
            "total_debe": m["total_debe"],
            "total_haber": m["total_haber"],
            "saldo": m["saldo"]
        } for m in mayores])

        # Mostrar métricas generales
        total_debe = df["total_debe"].sum()
        total_haber = df["total_haber"].sum()
        colA, colB, colC = st.columns(3)
        with colA:
            st.metric("📊 Cuentas mayores", len(df))
        with colB:
            st.metric("💰 Total Débitos", f"${total_debe:,.2f}")
        with colC:
            st.metric("💰 Total Créditos", f"${total_haber:,.2f}")

        st.markdown("---")
        st.dataframe(df.sort_values("codigo_mayor").rename(columns={
            "codigo_mayor": "Código mayor",
            "nombre_mayor": "Nombre",
            "total_debe": "Total Debe",
            "total_haber": "Total Haber",
            "saldo": "Saldo (abs)"
        }), use_container_width=True)

        # Expanders: detalle por mayor (si incluir_detalle fue False, subcuentas estará vacío)
        st.markdown("---")
        st.subheader("Detalle por cuenta mayor")
        for m in mayores:
            with st.expander(f"{m['codigo_mayor']} — {m['nombre_mayor']}  |  Saldo: {m['saldo']}"):
                st.write(f"Total Debe: {m['total_debe']} — Total Haber: {m['total_haber']}")
                if m.get("subcuentas"):
                    sdf = pd.DataFrame(m["subcuentas"])
                    sdf = sdf[["codigo_cuenta", "nombre_cuenta", "total_debe", "total_haber", "saldo"]]
                    sdf = sdf.rename(columns={
                        "codigo_cuenta": "Código",
                        "nombre_cuenta": "Nombre",
                        "total_debe": "Total Debe",
                        "total_haber": "Total Haber",
                        "saldo": "Saldo"
                    })
                    st.dataframe(sdf.sort_values("Código"), use_container_width=True)
                else:
                    st.info("No hay subcuentas (o no se solicitó detalle).")


def mostrar_subcuentas(backend_url: str):
    """Tab: Subcuentas detallas (permite buscar por mayor y ver todas las subcuentas)"""
    st.subheader("Subcuentas detalladas (drill-down)")

    col1, col2 = st.columns(2)
    with col1:
        digitos = st.number_input("Dígitos para identificar mayor", min_value=1, max_value=10, value=4)
    with col2:
        codigo_mayor = st.text_input("Código mayor (opcional) — si vacío muestra todas", value="")

    fecha_inicio = st.date_input("Fecha inicio (subcuentas)", value=None, key="subs_fi")
    fecha_fin = st.date_input("Fecha fin (subcuentas)", value=None, key="subs_ff")
    if st.button("🔎 Cargar Subcuentas"):
        fi = fecha_inicio.isoformat() if fecha_inicio else None
        ff = fecha_fin.isoformat() if fecha_fin else None
        mayores = _consultar_api_libro_mayor(backend_url, digitos, fi, ff, True)
        if mayores is None:
            return
        if not mayores:
            st.info("No hay datos.")
            return

        # Si el usuario especificó un codigo_mayor, filtrar
        if codigo_mayor:
            mayores = [m for m in mayores if m["codigo_mayor"] == codigo_mayor]

        # Construir DataFrame con subcuentas concatenadas
        filas = []
        for m in mayores:
            for s in m.get("subcuentas", []):
                filas.append({
                    "codigo_mayor": m["codigo_mayor"],
                    "codigo_subcuenta": s["codigo_cuenta"],
                    "nombre_subcuenta": s["nombre_cuenta"],
                    "debe": s["total_debe"],
                    "haber": s["total_haber"],
                    "saldo": s["saldo"]
                })
        if not filas:
            st.info("No se encontraron subcuentas para los criterios.")
            return

        sdf = pd.DataFrame(filas)
        st.dataframe(sdf.sort_values(["codigo_mayor", "codigo_subcuenta"]), use_container_width=True)


def exportar_libro_mayor(backend_url: str):
    """Tab: Exportar libro mayor (genera Excel o HTML localmente desde la respuesta del backend)"""
    st.subheader("Exportar Libro Mayor")

    col1, col2 = st.columns(2)
    with col1:
        digitos = st.number_input("Dígitos para cuenta mayor", min_value=1, max_value=10, value=4, key="exp_digitos")
    with col2:
        formato = st.selectbox("Formato", ["excel", "html"])

    fecha_inicio = st.date_input("Fecha inicio (exportar)", value=None, key="exp_fi")
    fecha_fin = st.date_input("Fecha fin (exportar)", value=None, key="exp_ff")
    incluir_detalle = st.checkbox("Incluir subcuentas", value=True, key="exp_detalle")

    if st.button("📤 Generar archivo"):
        fi = fecha_inicio.isoformat() if fecha_inicio else None
        ff = fecha_fin.isoformat() if fecha_fin else None

        mayores = _consultar_api_libro_mayor(backend_url, digitos, fi, ff, incluir_detalle, timeout=60)
        if mayores is None:
            return
        if not mayores:
            st.info("No hay datos para exportar.")
            return

        # Construir DataFrame principal
        df_mayores = pd.DataFrame([{
            "codigo_mayor": m["codigo_mayor"],
            "nombre_mayor": m["nombre_mayor"],
            "total_debe": m["total_debe"],
            "total_haber": m["total_haber"],
            "saldo": m["saldo"]
        } for m in mayores])

        if formato == "excel":
            # Generar libro Excel con dos hojas: Resumen y Subcuentas
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_mayores.to_excel(writer, sheet_name="Resumen", index=False)

                # subcuentas hoja
                filas = []
                for m in mayores:
                    for s in m.get("subcuentas", []):
                        filas.append({
                            "codigo_mayor": m["codigo_mayor"],
                            "codigo_subcuenta": s["codigo_cuenta"],
                            "nombre_subcuenta": s["nombre_cuenta"],
                            "total_debe": s["total_debe"],
                            "total_haber": s["total_haber"],
                            "saldo": s["saldo"]
                        })
                if filas:
                    df_subs = pd.DataFrame(filas)
                    df_subs.to_excel(writer, sheet_name="Subcuentas", index=False)
                else:
                    # Crear DataFrame vacío con columnas esperadas
                    df_empty = pd.DataFrame(columns=["codigo_mayor", "codigo_subcuenta", "nombre_subcuenta", "total_debe", "total_haber", "saldo"])
                    df_empty.to_excel(writer, sheet_name="Subcuentas", index=False)

            buffer.seek(0)
            st.download_button(
                label="📥 Descargar Excel",
                data=buffer.getvalue(),
                file_name="libro_mayor.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:
            # HTML: resumen + subcuentas
            html = "<h1>Libro Mayor - Resumen</h1>"
            html += df_mayores.to_html(index=False)
            filas = []
            for m in mayores:
                for s in m.get("subcuentas", []):
                    filas.append({
                        "codigo_mayor": m["codigo_mayor"],
                        "codigo_subcuenta": s["codigo_cuenta"],
                        "nombre_subcuenta": s["nombre_cuenta"],
                        "total_debe": s["total_debe"],
                        "total_haber": s["total_haber"],
                        "saldo": s["saldo"]
                    })
            html += "<h2>Subcuentas</h2>"
            if filas:
                df_subs = pd.DataFrame(filas)
                html += df_subs.to_html(index=False)
            else:
                html += "<p>No se encontraron subcuentas para los criterios seleccionados.</p>"

            st.download_button(
                label="📥 Descargar HTML",
                data=html,
                file_name="libro_mayor.html",
                mime="text/html"
            )
