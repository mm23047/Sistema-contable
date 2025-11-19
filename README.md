# 💰 Sistema Contable Completo

Sistema de contabilidad integral con módulos de facturación, gestión de clientes, inventario y reportes contables, desarrollado con arquitectura moderna y desplegado con Docker.

---

## 📑 Índice

1. [Descripción General](#-descripción-general)
2. [Inicio Rápido](#-inicio-rápido)
3. [Interfaz de Usuario (Frontend)](#-interfaz-de-usuario-frontend)
4. [Características Principales](#-características-principales)
5. [Arquitectura y Tecnologías](#-arquitectura-y-tecnologías)
6. [API Endpoints](#-api-endpoints)
7. [Cambios Recientes](#-cambios-recientes-y-migraciones)
8. [Troubleshooting](#-troubleshooting)
9. [Pruebas Unitarias](#-pruebas-unitarias)

---

## 🎯 Descripción General

Sistema de contabilidad profesional que integra:

- ✅ **Contabilidad completa**: Transacciones, asientos contables, libro diario y mayor
- ✅ **Facturación normalizada**: Clientes, productos/servicios, facturas con detalles
- ✅ **Reportes profesionales**: PDFs fiscales, Excel, JSON, HTML
- ✅ **Catálogo de cuentas**: 294 cuentas preconfiguradas
- ✅ **Períodos contables**: Gestión mensual, trimestral y anual
- ✅ **Multi-formato**: Exportación en PDF, Excel, HTML y JSON

---

## 🚀 Inicio Rápido

### Prerrequisitos

- **Docker Desktop** (con Docker Compose)
- **Git**
- Windows 10/11, macOS o Linux

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/mm23047/Sistema-contable.git
cd Sistema-contable
```

### 2️⃣ Configurar Variables de Entorno

Edita el archivo `.env`:

```env
# Puertos
PORT_BE=8000
PORT_FE=8501

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_DB=contable_db
POSTGRES_HOST=contable_db17
POSTGRES_PORT=5432

# PgAdmin
PGADMIN_EMAIL=tu_email@ejemplo.com
PGADMIN_PASSWORD=tu_password_admin
PGADMIN_PORT=5050
```

### 3️⃣ Levantar los Contenedores

```bash
docker compose up --build -d
docker compose ps  # Verificar servicios
```

### 4️⃣ Inicializar la Base de Datos

```powershell
# Windows PowerShell
Get-Content "inicializacion_completa_bd.sql" | docker exec -i contable_db17 psql -U postgres -d contable_db
```

```bash
# Linux/macOS
cat inicializacion_completa_bd.sql | docker exec -i contable_db17 psql -U postgres -d contable_db
```

### 5️⃣ Acceder al Sistema

| Servicio        | URL                        |
| --------------- | -------------------------- |
| **Frontend**    | http://localhost:8501      |
| **Backend API** | http://localhost:8000      |
| **Docs API**    | http://localhost:8000/docs |
| **pgAdmin**     | http://localhost:5050      |

---

## 🖥️ Interfaz de Usuario (Frontend)

El frontend está desarrollado con **Streamlit** y proporciona una interfaz intuitiva para gestionar todas las operaciones contables.

### 📌 Flujo de Trabajo Recomendado

```
1. CLIENTES → Registrar clientes antes de facturar
2. PRODUCTOS → Crear catálogo de productos/servicios
3. TRANSACCIONES → Registrar movimientos contables (Ingresos/Egresos)
4. ASIENTOS → Crear asientos contables asociados a transacciones
5. FACTURAS → Generar facturas desde transacciones o crear nuevas
6. REPORTES → Visualizar y exportar reportes contables
7. LIBRO MAYOR → Consultar balances y movimientos por cuenta
```

### 📄 Descripción de Páginas

#### 1. 🏢 **Clientes**

**Propósito**: Gestión completa del catálogo de clientes

**Funcionalidades**:

- **Tab "Ver Clientes"**: Lista todos los clientes con estadísticas (total de compras, facturas)
- **Tab "Agregar Cliente"**: Formulario para registrar nuevos clientes
  - Datos: Nombre, NIT, dirección, teléfono, email
  - Tipo: Individual o Empresa
  - Estado: Activo/Inactivo
- **Tab "Editar Cliente"**: Modificar datos de clientes existentes
- **Estadísticas**: Resumen de clientes activos, total registrado

**Flujo**:

1. Navegar a "Clientes"
2. Crear cliente nuevo en tab "Agregar Cliente"
3. Verificar en tab "Ver Clientes" que se agregó correctamente
4. Usar cliente al crear facturas

---

#### 2. 📦 **Productos**

**Propósito**: Administración del inventario de productos y servicios

**Funcionalidades**:

- **Tab "Ver Productos"**: Catálogo completo con filtros
  - Filtrar por tipo (Producto/Servicio)
  - Filtrar por estado (Activo/Inactivo)
  - Ver stock actual y alertas de stock mínimo
- **Tab "Agregar Producto"**: Crear nuevos ítems
  - Código SKU único
  - Nombre y descripción
  - Categoría personalizable
  - Precios: Unitario y costo
  - Control de stock (actual y mínimo)
  - Indicador de IVA
- **Tab "Editar Producto"**: Actualizar información
- **Tab "Estadísticas"**: Métricas de inventario
  - Total de productos activos
  - Valor total del inventario
  - Productos más vendidos
  - Alertas de stock bajo

**Flujo**:

1. Registrar productos en tab "Agregar Producto"
2. Configurar precios y stock
3. Usar productos al crear facturas con detalles

---

#### 3. 💵 **Transacciones**

**Propósito**: Registro de movimientos contables (origen de la contabilidad)

**Funcionalidades**:

- **Crear Transacción**: Formulario con validación
  - Fecha de transacción
  - Descripción detallada
  - Tipo: INGRESO o EGRESO
  - Categoría (Ventas, Compras, Servicios, etc.)
  - Usuario que registra
  - Período contable asociado
- **Listar Transacciones**: Tabla con todas las transacciones
  - Filtros por fecha, tipo, categoría
  - Acciones: Editar, Eliminar
- **Selección Automática**: Al crear una transacción, queda seleccionada para crear asientos

**Flujo**:

1. Seleccionar tipo (INGRESO/EGRESO)
2. Llenar descripción y datos
3. Guardar → La transacción queda "activa" en sesión
4. Ir a "Asientos" para registrar movimientos contables

**⚠️ Regla Importante**: Debes crear primero una transacción antes de poder crear asientos.

---

#### 4. 📊 **Asientos**

**Propósito**: Registro de movimientos de partida doble

**Funcionalidades**:

- **Crear Asiento**: Solo si hay transacción seleccionada
  - Seleccionar cuenta del catálogo (294 cuentas disponibles)
  - Especificar Debe o Haber
  - Monto del movimiento
  - Validación: Solo uno de Debe/Haber puede ser > 0
- **Ver Asientos de Transacción**: Lista de asientos asociados
  - Filtrar por transacción
  - Ver totales de Debe y Haber
  - Validación de balance (Debe = Haber)
- **Editar/Eliminar**: Modificar asientos existentes

**Flujo**:

1. Tener transacción creada (desde página "Transacciones")
2. Seleccionar cuenta contable
3. Ingresar monto en Debe o Haber
4. Repetir hasta balancear (Debe = Haber)
5. Verificar balance antes de cerrar

**⚠️ Validación**: El sistema verifica que exactamente uno de Debe/Haber sea mayor a cero.

---

#### 5. 🧾 **Facturas**

**Propósito**: Generación y gestión de facturas fiscales

**Funcionalidades**:

- **Tab "Listado de Facturas"**: Visualización completa
  - Expandir cada factura para ver detalles completos
  - Información del cliente (normalizada)
  - Detalles financieros (Subtotal, IVA, Descuento, Total)
  - **Botones de descarga**:
    - 📄 PDF: Factura fiscal profesional
    - 📊 Excel: Hoja de cálculo con formato
    - 📋 JSON: Datos estructurados con detalles
  - Filtros: Por cliente, NIT, fecha
- **Tab "Estadísticas"**: Análisis de facturación
  - Total facturado en período
  - IVA recaudado
  - Descuentos otorgados
  - Promedio de venta
  - Top clientes por volumen
- **Tab "Crear Factura"**: Formulario normalizado
  - **Sección 1: Seleccionar Cliente**
    - Dropdown con clientes registrados
    - Opción de crear cliente nuevo (abre modal)
  - **Sección 2: Agregar Productos** (fuera del form para interactividad)
    - Seleccionar producto del catálogo
    - Cantidad (actualiza en tiempo real)
    - Descuento opcional
    - Botón "➕ Agregar a Factura"
    - Botón "🗑️ Limpiar Todos los Productos"
  - **Sección 3: Tabla de Productos Agregados**
    - Ver líneas de la factura
    - Subtotales por producto
    - Total acumulado con IVA
  - **Sección 4: Información Adicional** (dentro del form)
    - Condiciones de pago (Contado/Crédito)
    - Vendedor
    - Fecha de vencimiento
    - Notas
    - Botón "✅ Crear Factura Completa"

**Flujo de Creación**:

1. Navegar a tab "Crear Factura"
2. Seleccionar cliente existente
3. Agregar productos uno por uno:
   - Seleccionar producto → se muestra precio
   - Ajustar cantidad → se actualiza total
   - Clic en "➕ Agregar a Factura"
4. Revisar tabla de productos agregados
5. Llenar información adicional (vendedor, condiciones de pago)
6. Clic en "✅ Crear Factura Completa"
7. Verificar en tab "Listado" que se creó correctamente

**Características Especiales**:

- Numeración automática: `FACT-2025-0001`
- Cálculo automático de IVA (13%)
- Validación de datos del cliente
- Integración con transacciones contables
- Productos seleccionables actualizan en tiempo real (fuera del form)

**Descargas Disponibles**:

- **PDF**: Incluye logo de empresa (placeholder), detalles de cliente, tabla de productos, totales y notas
- **Excel**: Formato profesional con hojas separadas para datos y detalles
- **JSON**: Estructura completa con metadata, detalles de productos y totales

---

#### 6. 📈 **Reportes**

**Propósito**: Visualización y exportación de reportes contables

**Funcionalidades**:

- **Libro Diario**: Registro cronológico de todas las operaciones
  - Filtros por fecha
  - Filtros por tipo de transacción
  - Ver asientos agrupados por transacción
  - Columnas: Fecha, Descripción, Cuenta, Debe, Haber
  - Totales calculados automáticamente
- **Exportaciones**:
  - 📊 Excel: Libro Diario formateado
  - 🌐 HTML: Reporte visual para navegador
- **Balances**: Resumen por período contable
  - Balance de comprobación
  - Estado de resultados
  - Balance general

**Flujo**:

1. Seleccionar rango de fechas
2. Aplicar filtros opcionales
3. Visualizar reporte en pantalla
4. Exportar en formato deseado

---

#### 7. 📚 **Libro Mayor**

**Propósito**: Consulta de movimientos por cuenta contable

**Funcionalidades**:

- **Seleccionar Cuenta**: Dropdown con catálogo de 294 cuentas
  - Agrupadas por tipo (Activo, Pasivo, Capital, Ingreso, Egreso)
  - Código y nombre de cuenta
- **Ver Movimientos**: Tabla de transacciones
  - Fecha y descripción
  - Debe y Haber
  - Saldo acumulado
- **Filtros**:
  - Por período contable
  - Por rango de fechas
- **Totales**:
  - Total Debe
  - Total Haber
  - Saldo Final

**Flujo**:

1. Seleccionar cuenta a consultar
2. Aplicar filtros de período
3. Revisar movimientos y saldo
4. Exportar si es necesario

---

### 🔄 Estado de Sesión

El frontend utiliza `st.session_state` para mantener:

- **transaccion_actual**: Transacción seleccionada para crear asientos
- **productos_factura**: Lista temporal de productos al crear factura
- **filtros activos**: Preserva filtros entre navegaciones

### 🎨 Características de UX

- **Diseño responsivo**: Layout ancho (`wide`)
- **Sidebar expandido**: Navegación siempre visible
- **Feedback visual**:
  - ✅ Mensajes de éxito en verde
  - ❌ Mensajes de error en rojo
  - ⚠️ Advertencias en amarillo
  - 💡 Información en azul
- **Validación en tiempo real**: Campos con validación inmediata
- **Confirmaciones**: Diálogos para acciones destructivas
- **Loading states**: Indicadores de carga en operaciones largas

---

## 📋 API Endpoints

### Endpoints Principales

**Facturas**:

- `GET /api/facturas/` - Listado con filtros (cliente, NIT, fechas)
- `POST /api/facturas/` - Crear factura nueva
- `GET /api/facturas/{id}` - Obtener factura específica
- `GET /api/facturas/{id}/descargar-pdf` - Descarga PDF
- `GET /api/facturas/{id}/descargar-excel` - Descarga Excel
- `GET /api/facturas/{id}/descargar-json` - Descarga JSON con detalles completos
- `GET /api/facturas/estadisticas/resumen` - Estadísticas de facturación
- `GET /api/facturas/estadisticas/top-clientes` - Top clientes

**Clientes**:

- `GET /api/clientes/` - Listar todos
- `POST /api/clientes/` - Crear cliente
- `PUT /api/clientes/{id}` - Actualizar
- `DELETE /api/clientes/{id}` - Eliminar

**Productos**:

- `GET /api/productos/` - Catálogo completo
- `POST /api/productos/` - Crear producto
- `PUT /api/productos/{id}` - Actualizar
- `GET /api/productos/estadisticas/resumen` - Métricas de inventario

**Transacciones y Asientos**:

- `POST /api/transacciones/` - Crear transacción
- `POST /api/asientos/` - Crear asiento contable
- `GET /api/reportes/libro-diario` - Libro diario

**Documentación interactiva**: http://localhost:8000/docs

---

## 📚 Características Principales

### 🧾 Facturación Normalizada

- Numeración automática: `FACT-2025-0001`
- Múltiples productos por factura con detalles
- Cálculo automático de IVA (13%)
- Descuentos por línea y globales
- Cliente normalizado con datos completos
- Exportación profesional (PDF, Excel, JSON)
- Estadísticas y top clientes

### 💼 Gestión de Clientes

- CRUD completo
- Tipos: Individual / Empresa
- Estado: Activo / Inactivo
- Historial de compras
- Estadísticas integradas

### 📦 Catálogo de Productos/Servicios

- Código SKU único
- Control de inventario (stock actual/mínimo)
- Categorías personalizables
- Indicador de IVA
- Tipos: Producto / Servicio
- Alertas de stock bajo

### 📊 Contabilidad Completa

- Transacciones (Ingreso/Egreso)
- Asientos contables (partida doble)
- Validación: Debe = Haber
- Catálogo de 294 cuentas
- Períodos contables
- Libro Diario y Mayor

### 📈 Reportes Multi-formato

- Exportación PDF, Excel, HTML, JSON
- Filtros por período y tipo
- Estadísticas en tiempo real
- Balances automáticos

---

## 🏗️ Arquitectura y Tecnologías

### Stack Tecnológico

**Backend**:

- FastAPI (framework web asíncrono)
- SQLAlchemy (ORM)
- Pydantic v2 (validación con `field_validator`, `from_attributes`)
- PostgreSQL 17.5
- ReportLab (generación de PDFs)
- openpyxl (archivos Excel)
- Uvicorn (servidor ASGI)

**Frontend**:

- Streamlit (interfaz interactiva)
- Pandas (procesamiento de datos)
- Requests (cliente HTTP)

**Infraestructura**:

- Docker y Docker Compose
- pgAdmin 4 (administración BD)

### Estructura del Proyecto

```
proyecto-contable/
├── BE/                        # Backend FastAPI
│   ├── app/
│   │   ├── main.py           # App principal
│   │   ├── db.py             # Configuración BD
│   │   ├── models/           # Modelos SQLAlchemy
│   │   │   ├── cliente.py
│   │   │   ├── producto_servicio.py
│   │   │   ├── factura_models.py
│   │   │   ├── factura_detalle.py
│   │   │   ├── transaccion.py
│   │   │   ├── asiento.py
│   │   │   ├── catalogo_cuentas.py
│   │   │   └── periodo.py
│   │   ├── schemas/          # Esquemas Pydantic v2
│   │   ├── routes/           # Endpoints API
│   │   └── services/         # Lógica de negocio
│   └── requirements.txt
│
├── FE/                        # Frontend Streamlit
│   ├── app.py                # App principal
│   ├── modules/              # Páginas del sistema
│   │   ├── transacciones.py
│   │   ├── asientos.py
│   │   ├── facturas.py       #
│   │   ├── clientes.py       #
│   │   ├── productos.py      #
│   │   ├── reportes.py
│   │   └── libro_mayor.py
│   └── requirements.txt
│
├── docker-compose.yml
├── .env
├── inicializacion_completa_bd.sql

```

---

## 🔄 Cambios Recientes y Migraciones

### Normalización de Base de Datos (v2.0)

**Tablas Nuevas**:

- `clientes` - Catálogo de clientes reutilizable
- `productos_servicios` - Inventario completo
- `factura_detalle` - Líneas de productos por factura

**Cambios en Facturas**:

- Relación normalizada con `clientes` (`id_cliente`)
- Detalles de productos en tabla separada
- Campos legacy mantenidos para compatibilidad
- Endpoint JSON agregado para descarga completa

**Migración a Pydantic v2**:

- `@validator` → `@field_validator` + `@classmethod`
- `values` → `info.data`
- `orm_mode` → `from_attributes`

**Correcciones SQLAlchemy**:

- `func.now()` → `func.current_timestamp()` en `server_default`
- Relaciones bidireccionales corregidas (`back_populates`)

**Scripts de Migración**:

- `inicializacion_completa_bd.sql`: Setup completo desde cero

---

## 🔧 Troubleshooting

### Problemas Comunes

**1. Cambios en frontend no aparecen**

- Reconstruir sin caché: `docker compose build --no-cache frontend`
- Reiniciar contenedores: `docker compose restart frontend`

**2. Errores de Pydantic v2 / Pylint**

- Pylint puede marcar falsos positivos con `@field_validator` + `@classmethod`
- Si el código funciona, agregar: `# pylint: disable=no-self-argument`
- Recargar ventana de VS Code si persiste

**3. Errores al generar PDF/Excel**

- Verificar instalación: `reportlab` y `openpyxl` en `BE/requirements.txt`
- Reconstruir contenedor backend con `--no-cache`

**4. Error de conexión a base de datos**

- Verificar que el contenedor `contable_db17` esté corriendo
- Revisar variables de entorno en `.env`
- Comprobar logs: `docker compose logs db`

**5. Numeración de facturas incorrecta**

- Verificar secuencia en BD: `SELECT nextval('factura_numero_seq')`
- Reiniciar secuencia si es necesario

**6. Productos no se agregan a factura**

- Recordar que selectores de productos están **fuera del formulario** para actualización en tiempo real
- Hacer clic en "➕ Agregar a Factura" después de seleccionar

---

## 🛠️ Desarrollo Local

### Ejecutar sin Docker

**Backend**:

```bash
cd BE
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**:

```bash
cd FE
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### Comandos Útiles

**Logs de contenedores**:

```bash
docker compose logs -f frontend  # Seguir logs del frontend
docker compose logs -f backend   # Seguir logs del backend
docker compose logs -f db        # Seguir logs de PostgreSQL
```

**Reiniciar servicios**:

```bash
docker compose restart frontend
docker compose restart backend
docker compose restart  # Todos los servicios
```

**Acceder a la base de datos**:

```bash
docker exec -it contable_db17 psql -U postgres -d contable_db
```

---

## 🧪 Pruebas Unitarias

El proyecto incluye **54 pruebas unitarias** funcionando al **100%** para backend y frontend ubicadas en `tests/`.

### Resultados de Pruebas

✅ **Frontend (Lógica de Negocio)**: **24/24 pruebas PASANDO** ✅

- `test_clientes.py`: 4 pruebas (validación NIT, email, teléfono, tipo cliente)
- `test_facturas.py`: 10 pruebas (cálculos, descuentos, IVA, validaciones)
- `test_productos.py`: 10 pruebas (precios, stock, margen, inventario)

✅ **Backend (API FastAPI)**: **30/30 pruebas PASANDO** (100% éxito) ✅

- ✅ `test_asientos.py`: **8/8 PASANDO** (100%) - asientos contables, validaciones de debe/haber
- ✅ `test_clientes.py`: **7/7 PASANDO** (100%) - CRUD completo, búsqueda por NIT, activar/desactivar
- ✅ `test_facturas.py`: **7/7 PASANDO** (100%) - creación, detalles, descuentos, IVA mixto
- ✅ `test_productos.py`: **3/3 PASANDO** (100%) - crear producto, servicio, listar
- ✅ `test_transacciones.py`: **5/5 PASANDO** (100%) - crear, validar tipo, descripción, listar con periodos

**Total Backend + Frontend**: **54/54 pruebas pasando (100%)** 🎉

### Configuración Implementada

✅ **Modo TEST configurado**: Las pruebas usan SQLite en memoria separado de PostgreSQL de producción  
✅ **Aislamiento completo**: Cada test crea y destruye su propia base de datos  
✅ **Sin afectar producción**: Los datos de prueba nunca tocan la BD de producción

### Estructura de Tests

```
tests/
├── be/                 # Tests del Backend (FastAPI)
│   ├── test_transacciones.py
│   ├── test_asientos.py
│   ├── test_clientes.py
│   ├── test_productos.py
│   └── test_facturas.py
└── fe/                 # Tests del Frontend (lógica de negocio)
    ├── test_clientes.py
    ├── test_productos.py
    └── test_facturas.py
```

### Ejecutar Pruebas

**✅ Sistema Funcionando**: Las pruebas usan SQLite en memoria, completamente separado de PostgreSQL de producción.

**Comandos para ejecutar pruebas:**

```powershell
# Windows PowerShell (Recomendado)
$env:PYTHONPATH="."; venv\Scripts\python.exe -m pytest tests/be/ -v
$env:PYTHONPATH="."; venv\Scripts\python.exe -m pytest tests/fe/ -v

# Ejecutar archivo específico
$env:PYTHONPATH="."; venv\Scripts\python.exe -m pytest tests/be/test_productos.py -v
$env:PYTHONPATH="."; venv\Scripts\python.exe -m pytest tests/be/test_clientes.py -v

# Todas las pruebas (Backend + Frontend)
$env:PYTHONPATH="."; venv\Scripts\python.exe -m pytest tests/ -v

# Con reporte de cobertura
$env:PYTHONPATH="."; venv\Scripts\python.exe -m pytest tests/be/ --cov=BE.app --cov-report=html
```

```bash
# Linux/Mac
PYTHONPATH=. pytest tests/be/ -v
PYTHONPATH=. pytest tests/fe/ -v
```

**Requisitos previos:**

```bash
# Instalar dependencias del backend en el venv
pip install -r BE/requirements.txt

# O instalar manualmente
pip install pytest httpx fastapi sqlalchemy pydantic reportlab pandas
```

---

### 🔧 Detalles Técnicos de Implementación

**Modo TEST configurado en el código:**

1. **`BE/app/db.py`**: Detecta variable `TESTING` y usa SQLite en memoria
2. **`BE/app/main.py`**: No ejecuta `create_tables()` en modo test
3. **Tests**: Configuran `os.environ["TESTING"] = "true"` antes de importar app
4. **Aislamiento**: Cada test crea/destruye su BD independiente

**Archivos modificados para soportar pruebas:**

- `BE/app/db.py`: Lógica condicional para SQLite/PostgreSQL
- `BE/app/main.py`: Skip de startup event en modo test
- `tests/be/*.py`: Configuración de fixtures con engine compartido

---

### Dependencias de Pruebas

```txt
pytest>=9.0.0
httpx>=0.24.0
fastapi
sqlalchemy
pydantic
```

### Estructura de Tests

```
tests/
├── be/                      # Tests del backend
│   ├── test_transacciones.py
│   └── test_asientos.py
└── fe/                      # Tests del frontend (por implementar)
```

**Nota**: Las pruebas usan SQLite en memoria para no afectar la base de datos PostgreSQL de desarrollo.

---

**Última actualización**: Noviembre 2025 | **Versión**: 2.0 (Normalización)

---

Para más información, consulta la documentación interactiva de la API en http://localhost:8000/docs después de levantar los servicios.
