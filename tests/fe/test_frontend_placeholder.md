# Placeholder para Pruebas del Frontend

## Estrategia de Pruebas para Frontend Streamlit

Este archivo sirve como placeholder para la implementación de pruebas del frontend.

### Cobertura de Pruebas Planificada

#### Pruebas Unitarias

- [ ] Probar funciones utilitarias para comunicación con API
- [ ] Probar lógica de validación de datos
- [ ] Probar manejadores de envío de formularios

#### Pruebas de Integración

- [ ] Probar renderizado de páginas con respuestas de API simuladas
- [ ] Probar flujo de usuario: Transacción → Asiento → Reporte
- [ ] Probar manejo de errores y retroalimentación al usuario

#### Pruebas End-to-End

- [ ] Probar el recorrido completo del usuario con backend real
- [ ] Probar funcionalidad de descarga de archivos
- [ ] Probar diseño responsivo en diferentes tamaños de pantalla

### Opciones de Framework de Pruebas

1. **Streamlit Testing Framework** (cuando esté disponible)
2. **Selenium WebDriver** para automatización de navegador
3. **pytest** con componentes Streamlit simulados
4. **playwright** para pruebas de navegador modernas

### Estado Actual

Las pruebas del frontend no están implementadas actualmente. Las siguientes áreas necesitan pruebas:

- `app.py` - Enrutamiento de aplicación principal
- `pages/transacciones.py` - Gestión de transacciones
- `pages/asientos.py` - Gestión de asientos contables
- `pages/reportes.py` - Generación y exportación de reportes

### TODO de Implementación

```python
# Ejemplo de estructura de prueba:

def test_transaction_form_validation():
    """Probar validación del lado del cliente para formulario de transacciones"""
    pass

def test_asiento_balance_calculation():
    """Probar cálculo de balance debe/haber"""
    pass

def test_report_export_functionality():
    """Probar funcionalidades de exportación Excel/HTML"""
    pass
```

### Lista de Verificación de Pruebas Manuales

Hasta que se implementen las pruebas automatizadas, usa esta lista de verificación manual:

#### Página de Transacciones

- [ ] Crear transacción con todos los campos
- [ ] Crear transacción con campos mínimos requeridos
- [ ] Validar mensajes de error para entrada inválida
- [ ] Probar selección de transacción para asientos

#### Página de Asientos

- [ ] Crear asiento debe con transacción válida
- [ ] Crear asiento haber con transacción válida
- [ ] Probar validación cuando no hay transacción seleccionada
- [ ] Probar carga del dropdown de cuentas
- [ ] Probar visualización del cálculo de balance

#### Página de Reportes

- [ ] Generar reporte de libro diario
- [ ] Exportar archivo Excel y verificar contenido
- [ ] Exportar archivo HTML y verificar formato
- [ ] Probar reporte de balance por período
- [ ] Verificar mensajes de validación de balance

#### UI/UX General

- [ ] Probar diseño responsivo en móvil
- [ ] Probar manejo de errores por problemas de conectividad backend
- [ ] Probar gestión de estado de sesión
- [ ] Probar navegación entre páginas
