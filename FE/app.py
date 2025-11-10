"""
Aplicación principal Streamlit para el frontend del sistema contable.
Proporciona una interfaz web para gestionar transacciones, asientos contables y reportes.
"""
import streamlit as st
import os
from modules import transacciones, asientos, reportes

# Configurar ajustes de página
st.set_page_config(
    page_title="Sistema Contable",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de URL del backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Título principal de la aplicación
st.title("💰 Sistema Contable")
st.markdown("---")

# Navegación del sidebar
st.sidebar.title("Navegación")
page = st.sidebar.selectbox(
    "Selecciona una página:",
    ["Transacciones", "Asientos", "Reportes"]
)

# Inicializar estado de sesión
if "transaccion_actual" not in st.session_state:
    st.session_state.transaccion_actual = None

# Enrutamiento de páginas
if page == "Transacciones":
    transacciones.render_page(BACKEND_URL)
elif page == "Asientos":
    asientos.render_page(BACKEND_URL)
elif page == "Reportes":
    reportes.render_page(BACKEND_URL)

# Mostrar información de transacción actual en sidebar
if st.session_state.transaccion_actual:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Transacción Actual:**")
    st.sidebar.markdown(f"ID: {st.session_state.transaccion_actual}")
    if st.sidebar.button("Limpiar Transacción"):
        st.session_state.transaccion_actual = None
        st.rerun()
else:
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Selecciona una transacción para crear asientos")

# Pie de página
st.markdown("---")
st.markdown(
    "📊 Sistema Contable - Flujo: Crear Transacción → Crear Asientos → Reportes",
    help="Sigue el flujo obligatorio: primero crea una transacción, luego los asientos asociados"
)