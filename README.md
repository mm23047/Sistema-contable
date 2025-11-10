# 💰 Sistema Contable

Un sistema de contabilidad completo desarrollado con FastAPI (backend), Streamlit (frontend), y PostgreSQL (base de datos).

## 🚀 Características

- **Backend**: FastAPI con SQLAlchemy y PostgreSQL
- **Frontend**: Streamlit con interfaz web intuitiva
- **Base de datos**: PostgreSQL 17.5 con pgAdmin
- **Flujo contable completo**: Transacciones → Asientos → Reportes
- **Exportación**: Libro Diario en Excel y HTML
- **Dockerizado**: Despliegue completo con Docker Compose
- **Catálogo completo**: 288 cuentas contables preconfiguradas

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Docker Desktop
- Git

### 1. Clonar el repositorio

```bash
git clone <url-de-tu-repositorio>
cd proyecto-contable
```

### 2. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# POSTGRES_PASSWORD=tu_password_seguro
# PGADMIN_EMAIL=tu_email@ejemplo.com
# PGADMIN_PASSWORD=tu_password_admin
```

### 3. Levantar los servicios

```bash
# Construir y ejecutar todos los contenedores
docker-compose up --build

# O en segundo plano
docker-compose up -d --build
```

### 4. Inicializar la base de datos

```bash
# Opción 1: Script básico (primeras cuentas)
Get-Content "init_database.sql" | docker exec -i contable_db17 psql -U postgres -d contable_db

# Opción 2: Para cargar el catálogo completo (288 cuentas)
# Usar el archivo insert_catalogo.sql proporcionado por el usuario
```

## 🌐 Acceso al Sistema

Una vez que todos los servicios estén ejecutándose:

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

## 📊 Uso del Sistema

### 1. Gestión de Transacciones

- Crear transacciones de INGRESO o EGRESO
- Asociar a períodos contables
- Validación automática de datos

### 2. Asientos Contables

- Crear asientos debe/haber
- Validación de partida doble
- Asociar a cuentas del catálogo

### 3. Reportes

- Libro Diario completo
- Exportación a Excel/HTML
- Filtros por período

## 🏗️ Arquitectura

```
proyecto-contable/
├── BE/                     # Backend FastAPI
│   ├── app/
│   │   ├── main.py        # Aplicación principal
│   │   ├── db.py          # Configuración de base de datos
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── schemas/       # Esquemas Pydantic
│   │   ├── routes/        # Endpoints API
│   │   └── services/      # Lógica de negocio
│   ├── requirements.txt
│   └── Dockerfile
├── FE/                     # Frontend Streamlit
│   ├── app.py             # Aplicación principal
│   ├── pages/             # Páginas de la interfaz
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml      # Orquestación de servicios
├── .env.example           # Variables de entorno
└── README.md
```

## 🛠️ Instalación y Despliegue

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd proyecto-contable
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Levantar los Servicios

```bash
docker-compose up --build
```

## 🌐 URLs de Acceso

Una vez iniciados los servicios:

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API (FastAPI)**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

## 📊 Flujo de Uso

### Flujo Obligatorio

1. **Crear Transacción** → Registra una nueva transacción contable
2. **Crear Asientos** → Solo después de tener una transacción, crea los asientos asociados
3. **Editar/Eliminar** → Modifica transacciones y asientos según sea necesario
4. **Generar Reportes** → Visualiza y exporta el Libro Diario

### Pasos Detallados

#### 1. Gestión de Transacciones

- Navega a la página "Transacciones"
- Llena el formulario con fecha, descripción, tipo (INGRESO/EGRESO), usuario, etc.
- Al crear exitosamente, la transacción queda seleccionada para asientos

#### 2. Gestión de Asientos

- Navega a la página "Asientos" (solo disponible con transacción seleccionada)
- Selecciona una cuenta del catálogo
- Especifica si es Débito o Crédito y el monto
- El sistema valida que exactamente uno de debe/haber sea > 0

#### 3. Reportes y Exportación

- Navega a la página "Reportes"
- Visualiza el Libro Diario con todos los asientos
- Exporta en formato Excel o HTML
- Revisa balances por período

## 🔧 API Examples

### Crear Transacción

```bash
curl -X POST "http://localhost:8000/api/transacciones/" \
     -H "Content-Type: application/json" \
     -d '{
       "fecha_transaccion": "2025-08-01T10:00:00",
       "descripcion": "Venta de camisetas",
       "tipo": "INGRESO",
       "moneda": "USD",
       "usuario_creacion": "estudiante1",
       "id_periodo": 1
     }'
```

**Respuesta 201:**

```json
{
  "id_transaccion": 12
}
```

### Crear Asiento

```bash
curl -X POST "http://localhost:8000/api/asientos/" \
     -H "Content-Type: application/json" \
     -d '{
       "id_transaccion": 12,
       "id_cuenta": 3,
       "debe": 50.00,
       "haber": 0.00
     }'
```

**Respuesta 201:**

```json
{
  "id_asiento": 45
}
```

## 📋 Validaciones y Reglas de Negocio

### Transacciones

- Fecha debe ser formato ISO válido
- Tipo debe ser 'INGRESO' o 'EGRESO'
- Descripción y usuario son obligatorios

### Asientos

- Debe existir la transacción asociada (FK validation)
- Debe existir la cuenta asociada (FK validation)
- **Regla crítica**: Exactamente uno de `debe` o `haber` debe ser > 0
- No se permite crear asientos sin transacción

### Eliminación

- **TODO**: Definir política de cascada al eliminar transacciones
- Actualmente implementa eliminación en cascada
- Considerar marcar como inactivo en lugar de eliminar

## 🧪 Desarrollo

### Ejecutar Backend Localmente

```bash
cd BE
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Ejecutar Frontend Localmente

```bash
cd FE
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### Ejecutar Pruebas

```bash
# TODO: Implementar framework de pruebas
python -m pytest tests/
```

## 🐛 Tareas Pendientes (TODO)

### Backend

- [ ] Implementar Alembic para migraciones en producción
- [ ] Configurar gunicorn/uvicorn workers para producción
- [ ] Implementar paginación para endpoints con muchos registros
- [ ] Añadir autenticación y autorización
- [ ] Mejorar manejo de errores con logs estructurados
- [ ] Implementar políticas de eliminación en cascada configurables

### Frontend

- [ ] Cargar períodos dinámicamente desde la API
- [ ] Implementar validaciones client-side más robustas
- [ ] Añadir gráficos y dashboards
- [ ] Implementar filtros avanzados en reportes
- [ ] Mejorar UX con loading states y confirmaciones

### General

- [ ] Configurar CI/CD pipeline
- [ ] Implementar backup automatizado de la base de datos
- [ ] Documentar API con ejemplos más detallados
- [ ] Añadir métricas y monitoreo
- [ ] Configurar CORS específicos para producción

## 📚 Tecnologías Utilizadas

- **Backend**: FastAPI, SQLAlchemy, psycopg2-binary, Pydantic
- **Frontend**: Streamlit, Requests, Pandas
- **Base de datos**: PostgreSQL 17.5
- **Administración DB**: pgAdmin 4
- **Containerización**: Docker, Docker Compose
- **Exportación**: openpyxl (Excel), Jinja2 (HTML)

## 🔒 Configuración de Producción

### Variables de Entorno Importantes

```bash
# En producción, usar valores seguros:
POSTGRES_PASSWORD=<contraseña-fuerte>
PGADMIN_PASSWORD=<contraseña-fuerte>

# Configurar CORS específicos
ALLOWED_ORIGINS=https://tu-dominio.com

# Configurar SSL para bases de datos
DATABASE_SSL=require
```

### Consideraciones de Seguridad

- Cambiar todas las contraseñas por defecto
- Configurar HTTPS/SSL para todos los servicios
- Implementar rate limiting en la API
- Configurar firewalls y acceso restringido a puertos
- Usar secretos de Docker/Kubernetes en lugar de .env

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Gitflow

- `main`: Código de producción estable
- `develop`: Rama de desarrollo principal
- `feature/*`: Nuevas funcionalidades
- `release/*`: Preparación de releases
- `hotfix/*`: Correcciones urgentes

## 📞 Soporte

Para reportar bugs o solicitar funcionalidades, por favor abre un issue en el repositorio.

---
