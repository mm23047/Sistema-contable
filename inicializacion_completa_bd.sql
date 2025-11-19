-- =============================================
-- SISTEMA CONTABLE - SCRIPT COMPLETO DE INICIALIZACIÓN Y MIGRACIÓN
-- =============================================
-- IMPORTANTE: Este script puede ejecutarse en dos escenarios:
-- 1. Base de datos NUEVA: Creará todas las tablas desde cero
-- 2. Base de datos EXISTENTE: Agregará tablas faltantes y migrará datos
-- 
-- INSTRUCCIONES:
-- 1. Abrir pgAdmin
-- 2. Conectarse a la base de datos 'contable_db'
-- 3. Abrir Query Tool (Tools > Query Tool)
-- 4. Copiar y pegar este script completo
-- 5. Ejecutar (F5 o botón Execute)
-- =============================================

-- =============================================
-- PASO 1: CREAR EXTENSIÓN PARA UUID (si no existe)
-- =============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- PASO 2: CREACIÓN DE TABLAS DEL SISTEMA CONTABLE
-- =============================================

-- Tabla: periodos_contables
CREATE TABLE IF NOT EXISTS public.periodos_contables (
    id_periodo SERIAL PRIMARY KEY,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    tipo_periodo VARCHAR(20) NOT NULL CHECK (tipo_periodo IN ('MENSUAL', 'TRIMESTRAL', 'ANUAL')),
    estado VARCHAR(10) DEFAULT 'ABIERTO' NOT NULL CHECK (estado IN ('ABIERTO', 'CERRADO')),
    CONSTRAINT periodo_valido CHECK (fecha_inicio <= fecha_fin)
);

-- Tabla: catalogo_cuentas
CREATE TABLE IF NOT EXISTS public.catalogo_cuentas (
    id_cuenta SERIAL PRIMARY KEY,
    codigo_cuenta VARCHAR(20) NOT NULL UNIQUE,
    nombre_cuenta VARCHAR(100) NOT NULL,
    tipo_cuenta VARCHAR(50) NOT NULL
);

-- Tabla: transacciones
CREATE TABLE IF NOT EXISTS public.transacciones (
    id_transaccion SERIAL PRIMARY KEY,
    fecha_transaccion TIMESTAMP NOT NULL,
    descripcion TEXT NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('INGRESO', 'EGRESO')),
    moneda VARCHAR(3) DEFAULT 'USD' NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50) NOT NULL,
    id_periodo INTEGER NOT NULL REFERENCES public.periodos_contables(id_periodo)
);

-- Tabla: asientos
CREATE TABLE IF NOT EXISTS public.asientos (
    id_asiento SERIAL PRIMARY KEY,
    id_transaccion INTEGER NOT NULL REFERENCES public.transacciones(id_transaccion),
    id_cuenta INTEGER NOT NULL REFERENCES public.catalogo_cuentas(id_cuenta),
    debe NUMERIC(15,2) DEFAULT 0.00,
    haber NUMERIC(15,2) DEFAULT 0.00,
    CONSTRAINT debe_o_haber CHECK (
        (debe > 0 AND haber = 0) OR 
        (haber > 0 AND debe = 0)
    )
);

-- =============================================
-- PASO 3: CREACIÓN DE TABLAS NORMALIZADAS (NUEVAS)
-- =============================================

-- Tabla: clientes
CREATE TABLE IF NOT EXISTS public.clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo_cliente VARCHAR(20) DEFAULT 'INDIVIDUAL' CHECK (tipo_cliente IN ('INDIVIDUAL', 'EMPRESA')),
    nit VARCHAR(20) UNIQUE,
    dui VARCHAR(20),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion VARCHAR(255),
    ciudad VARCHAR(100),
    departamento VARCHAR(100),
    codigo_postal VARCHAR(10),
    contacto_principal VARCHAR(100),
    activo VARCHAR(2) DEFAULT 'SI' CHECK (activo IN ('SI', 'NO')),
    notas TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: productos_servicios
CREATE TABLE IF NOT EXISTS public.productos_servicios (
    id_producto SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('PRODUCTO', 'SERVICIO')),
    categoria VARCHAR(100),
    precio_unitario NUMERIC(12, 2) NOT NULL,
    precio_costo NUMERIC(12, 2),
    unidad_medida VARCHAR(20) NOT NULL DEFAULT 'Unidad',
    stock_actual NUMERIC(12, 2) DEFAULT 0.00,
    stock_minimo NUMERIC(12, 2) DEFAULT 0.00,
    aplica_iva VARCHAR(2) DEFAULT 'SI' CHECK (aplica_iva IN ('SI', 'NO')),
    activo VARCHAR(2) DEFAULT 'SI' CHECK (activo IN ('SI', 'NO')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_stock_producto CHECK (
        (tipo = 'SERVICIO') OR 
        (tipo = 'PRODUCTO' AND stock_actual IS NOT NULL)
    )
);

-- Tabla: facturas (con campos legacy y normalizados)
CREATE TABLE IF NOT EXISTS public.facturas (
    id_factura UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_factura VARCHAR(50) NOT NULL UNIQUE,
    
    -- Cliente (legacy - mantener para compatibilidad)
    cliente VARCHAR(150),
    nit_cliente VARCHAR(20),
    direccion_cliente VARCHAR(255),
    telefono_cliente VARCHAR(20),
    email_cliente VARCHAR(100),
    
    -- Cliente (normalizado - NUEVO)
    id_cliente INTEGER REFERENCES public.clientes(id_cliente) ON DELETE SET NULL,
    
    -- Montos
    subtotal NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    descuento NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    iva NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    monto_total NUMERIC(12, 2) NOT NULL,
    
    -- Producto o Servicio (legacy - deprecado, usar factura_detalle)
    producto_servicio TEXT,
    
    -- Información adicional
    notas TEXT,
    condiciones_pago VARCHAR(100) DEFAULT 'Contado',
    vendedor VARCHAR(100),
    
    -- Fechas
    fecha_emision TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento TIMESTAMP,
    
    -- Relación con transacciones (opcional)
    id_transaccion INTEGER REFERENCES public.transacciones(id_transaccion)
);

-- Tabla: factura_detalle
CREATE TABLE IF NOT EXISTS public.factura_detalle (
    id_detalle SERIAL PRIMARY KEY,
    id_factura UUID NOT NULL REFERENCES public.facturas(id_factura) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL REFERENCES public.productos_servicios(id_producto) ON DELETE RESTRICT,
    cantidad NUMERIC(12, 2) NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12, 2) NOT NULL,
    descuento_porcentaje NUMERIC(5, 2) DEFAULT 0.00 CHECK (descuento_porcentaje >= 0 AND descuento_porcentaje <= 100),
    descuento_monto NUMERIC(12, 2) DEFAULT 0.00 CHECK (descuento_monto >= 0),
    subtotal NUMERIC(12, 2) NOT NULL,
    iva NUMERIC(12, 2) DEFAULT 0.00,
    total_linea NUMERIC(12, 2) NOT NULL
);

-- =============================================
-- PASO 4: CREACIÓN DE ÍNDICES
-- =============================================

-- Índices sistema contable
CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON public.transacciones(fecha_transaccion);
CREATE INDEX IF NOT EXISTS idx_asientos_transaccion ON public.asientos(id_transaccion);
CREATE INDEX IF NOT EXISTS idx_catalogo_codigo ON public.catalogo_cuentas(codigo_cuenta);

-- Índices clientes
CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON public.clientes(nombre);
CREATE INDEX IF NOT EXISTS idx_clientes_nit ON public.clientes(nit);
CREATE INDEX IF NOT EXISTS idx_clientes_activo ON public.clientes(activo);

-- Índices productos
CREATE INDEX IF NOT EXISTS idx_productos_codigo ON public.productos_servicios(codigo);
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON public.productos_servicios(nombre);
CREATE INDEX IF NOT EXISTS idx_productos_tipo ON public.productos_servicios(tipo);
CREATE INDEX IF NOT EXISTS idx_productos_activo ON public.productos_servicios(activo);

-- Índices facturas
CREATE INDEX IF NOT EXISTS idx_facturas_numero ON public.facturas(numero_factura);
CREATE INDEX IF NOT EXISTS idx_facturas_cliente_legacy ON public.facturas(cliente);
CREATE INDEX IF NOT EXISTS idx_facturas_id_cliente ON public.facturas(id_cliente);
CREATE INDEX IF NOT EXISTS idx_facturas_fecha ON public.facturas(fecha_emision);
CREATE INDEX IF NOT EXISTS idx_facturas_nit ON public.facturas(nit_cliente);

-- Índices factura_detalle
CREATE INDEX IF NOT EXISTS idx_detalle_factura ON public.factura_detalle(id_factura);
CREATE INDEX IF NOT EXISTS idx_detalle_producto ON public.factura_detalle(id_producto);

-- =============================================
-- MIGRACIÓN: Agregar columnas faltantes si no existen
-- =============================================

-- Agregar columna total_linea a factura_detalle si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'factura_detalle' 
        AND column_name = 'total_linea'
    ) THEN
        ALTER TABLE public.factura_detalle 
        ADD COLUMN total_linea NUMERIC(12, 2);
        
        -- Calcular valores existentes
        UPDATE public.factura_detalle 
        SET total_linea = subtotal + iva 
        WHERE total_linea IS NULL;
        
        -- Hacer NOT NULL después de calcular valores
        ALTER TABLE public.factura_detalle 
        ALTER COLUMN total_linea SET NOT NULL;
        
        RAISE NOTICE 'Columna total_linea agregada a factura_detalle';
    END IF;
END $$;

-- =============================================
-- PASO 5: INSERTAR DATOS INICIALES (solo si las tablas están vacías)
-- =============================================

-- Insertar períodos contables (solo si no existen)
INSERT INTO public.periodos_contables (fecha_inicio, fecha_fin, tipo_periodo, estado)
SELECT '2024-01-01'::DATE, '2024-12-31'::DATE, 'ANUAL', 'ABIERTO'
WHERE NOT EXISTS (SELECT 1 FROM public.periodos_contables WHERE fecha_inicio = '2024-01-01')
UNION ALL
SELECT '2025-01-01'::DATE, '2025-12-31'::DATE, 'ANUAL', 'ABIERTO'
WHERE NOT EXISTS (SELECT 1 FROM public.periodos_contables WHERE fecha_inicio = '2025-01-01')
UNION ALL
SELECT '2025-01-01'::DATE, '2025-01-31'::DATE, 'MENSUAL', 'ABIERTO'
WHERE NOT EXISTS (SELECT 1 FROM public.periodos_contables WHERE fecha_inicio = '2025-01-01' AND tipo_periodo = 'MENSUAL');

-- Insertar catálogo de cuentas (solo si está vacío)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.catalogo_cuentas LIMIT 1) THEN
        INSERT INTO public.catalogo_cuentas (codigo_cuenta, nombre_cuenta, tipo_cuenta) VALUES
        ('1', 'ACTIVO', 'ACTIVO'),
        ('11', 'ACTIVO CORRIENTE', 'ACTIVO'),
        ('1101', 'EFECTIVO Y EQUIVALENTES', 'ACTIVO'),
        ('110101', 'Caja', 'ACTIVO'),
        ('11010101', 'Caja General', 'ACTIVO'),
        ('11010102', 'Caja Chica', 'ACTIVO'),
        ('1101010201', 'Caja chica Casa Matriz', 'ACTIVO'),
        ('1101010202', 'Caja chica sucursal No. 1', 'ACTIVO'),
        ('110102', 'Bancos', 'ACTIVO'),
        ('110103', 'Equivalentes de efectivo', 'ACTIVO'),
        ('11010301', 'Depósitos a plazo', 'ACTIVO'),
        ('11010302', 'Operaciones de reporto', 'ACTIVO'),
        ('11010303', 'Voucher de Tarjetas de crédito', 'ACTIVO'),
        ('1102', 'CUENTAS Y DOCUMENTOS POR COBRAR', 'ACTIVO'),
        ('110201', 'Clientes', 'ACTIVO'),
        ('11020101', 'Clientes locales', 'ACTIVO'),
        ('11020102', 'Clientes del exterior', 'ACTIVO'),
        ('110202', 'Documentos por cobrar', 'ACTIVO'),
        ('11020201', 'Documentos por cobrar locales', 'ACTIVO'),
        ('11020202', 'Documentos por cobrar del exterior', 'ACTIVO'),
        ('110203', 'Cuentas por cobrar empleados', 'ACTIVO'),
        ('1103', 'ESTIMACION PARA CUENTAS INCOBRABLES (CR)', 'ACTIVO'),
        ('1104', 'PARTES RELACIONADAS POR COBRAR A CORTO PLAZO', 'ACTIVO'),
        ('110401', 'Casa matriz', 'ACTIVO'),
        ('110402', 'Sucursales', 'ACTIVO'),
        ('11040201', 'Sucursal 1', 'ACTIVO'),
        ('110403', 'Accionistas', 'ACTIVO'),
        ('110404', 'Directores y personal ejecutivo', 'ACTIVO'),
        ('110405', 'Subsidiarias', 'ACTIVO'),
        ('110406', 'Asociadas', 'ACTIVO'),
        ('1105', 'ARRENDAMIENTO FINANCIERO POR COBRAR A CORTO PLAZO', 'ACTIVO'),
        ('1106', 'ESTIMACION DE CUENTAS INCOBRABLES POR ARRENDAMIENTO', 'ACTIVO'),
        ('1107', 'INVENTARIOS', 'ACTIVO'),
        ('110701', 'Mercaderia para la venta', 'ACTIVO'),
        ('110702', 'Materias primas', 'ACTIVO'),
        ('110703', 'Producto en proceso', 'ACTIVO'),
        ('110704', 'Producto terminado', 'ACTIVO'),
        ('1108', 'PEDIDOS EN TRANSITO', 'ACTIVO'),
        ('1109', 'RESERVA PARA OBSOLESCENCIA DE INVENTARIOS (CR)', 'ACTIVO'),
        ('1110', 'INVERSIONES TEMPORALES', 'ACTIVO'),
        ('111001', 'Acciones', 'ACTIVO'),
        ('111002', 'Bonos', 'ACTIVO'),
        ('1111', 'PAGOS ANTICIPADOS', 'ACTIVO'),
        ('111101', 'Seguros pagados por anticipado', 'ACTIVO'),
        ('111102', 'Papelería y útiles', 'ACTIVO'),
        ('1112', 'CREDITO FISCAL - IVA', 'ACTIVO'),
        ('111201', 'Crédito Fiscal por Compras', 'ACTIVO'),
        ('11120101', 'Crédito fiscal por compras locales', 'ACTIVO'),
        ('11120102', 'Crédito fiscal por importaciones e internaciones', 'ACTIVO'),
        ('111202', 'Crédito Fiscal por Gastos', 'ACTIVO'),
        ('1113', 'PAGO A CUENTA DE IMPUESTOS', 'ACTIVO'),
        ('111301', 'ISR-Retenciones de Terceros', 'ACTIVO'),
        ('111302', 'ISR-Pago a Cuenta del Presente Ejercicio', 'ACTIVO'),
        ('111303', 'ISR-Pago a Cuenta de Ejercicios Anteriores', 'ACTIVO'),
        ('111304', 'ISR - Diferido', 'ACTIVO'),
        ('111305', 'Impuestos municipales', 'ACTIVO'),
        ('12', 'ACTIVO NO CORRIENTE', 'ACTIVO'),
        ('1201', 'CUENTAS POR COBRAR A LARGO PLAZO', 'ACTIVO'),
        ('1202', 'PARTES RELACIONADAS POR COBRAR A LARGO PLAZO', 'ACTIVO'),
        ('120201', 'Casa matriz', 'ACTIVO'),
        ('120202', 'Sucursales', 'ACTIVO'),
        ('120203', 'Accionistas', 'ACTIVO'),
        ('120204', 'Directores y ejecutivos', 'ACTIVO'),
        ('120205', 'Subsidiarias', 'ACTIVO'),
        ('120206', 'Asociadas', 'ACTIVO'),
        ('1203', 'ARRENDAMIENTO FINANCIERO POR COBRAR A LARGO PLAZO', 'ACTIVO'),
        ('1204', 'ESTIMACION DE CUENTAS INCOBRABLES POR ARRENDAMIENTO', 'ACTIVO'),
        ('1205', 'INVERSIONES PERMANENTES', 'ACTIVO'),
        ('120501', 'Acciones', 'ACTIVO'),
        ('120502', 'Bonos', 'ACTIVO'),
        ('1206', 'PROPIEDAD, PLANTA Y EQUIPO', 'ACTIVO'),
        ('120601', 'Bienes No Depreciables', 'ACTIVO'),
        ('12060101', 'Terrenos', 'ACTIVO'),
        ('120602', 'Bienes depreciables', 'ACTIVO'),
        ('12060201', 'Mobiliario y Equipo de Oficina', 'ACTIVO'),
        ('12060202', 'Equipo de transporte', 'ACTIVO'),
        ('12060203', 'Maquinaria', 'ACTIVO'),
        ('1207', 'DEPRECIACION ACUMULADA (CR)', 'ACTIVO'),
        ('120701', 'Depreciación acumulada de mobiliario y equipo', 'ACTIVO'),
        ('120702', 'Depreciación acumulada de equipo de transporte', 'ACTIVO'),
        ('120703', 'Depreciación acumulada de maquinaria', 'ACTIVO'),
        ('1208', 'PROPIEDAD DE INVERSIÓN', 'ACTIVO'),
        ('1209', 'DEPRECIACIÓN ACUMULADA DE PROPIEDAD DE INVERSION (CR)', 'ACTIVO'),
        ('1210', 'REVALUACIÓN DE ACTIVOS', 'ACTIVO'),
        ('121001', 'Terrenos (Revaluación)', 'ACTIVO'),
        ('121002', 'Edificaciones (Revaluación)', 'ACTIVO'),
        ('121003', 'Mobiliario y equipo de oficina (Revaluación)', 'ACTIVO'),
        ('121004', 'Equipo de transporte (Revaluación)', 'ACTIVO'),
        ('121005', 'Maquinaria (Revaluación)', 'ACTIVO'),
        ('1211', 'DEPRECIACIÓN ACUMULADA DE ACTIVOS REVALUADOS (CR)', 'ACTIVO'),
        ('1212', 'CONSTRUCCIONES EN PROCESO', 'ACTIVO'),
        ('1213', 'ACTIVOS BAJO ARRENDAMIENTO FINANCIERO', 'ACTIVO'),
        ('1214', 'DEP. ACUMULADA DE ACTIVO BAJO ARRENDAMIENTO (CR)', 'ACTIVO'),
        ('1215', 'ACTIVOS INTANGIBLES', 'ACTIVO'),
        ('121501', 'Programas de computadoras', 'ACTIVO'),
        ('121502', 'Patentes y marcas', 'ACTIVO'),
        ('121503', 'Licencias', 'ACTIVO'),
        ('1216', 'AMORTIZACIONES DE INTANGIBLES (CR)', 'ACTIVO'),
        ('121601', 'Programas de computadoras (Amortización)', 'ACTIVO'),
        ('121602', 'Marcas y patentes (Amortización)', 'ACTIVO'),
        ('121603', 'Licencias (Amortización)', 'ACTIVO'),
        ('1217', 'DEPOSITOS EN GARANTÍA', 'ACTIVO'),
        ('121701', 'Depósitos', 'ACTIVO'),
        ('1218', 'ACTIVO POR IMPUESTOS DIFERIDOS', 'ACTIVO'),
        ('2', 'PASIVO', 'PASIVO'),
        ('21', 'PASIVO CORRIENTE', 'PASIVO'),
        ('2101', 'PROVEEDORES LOCALES', 'PASIVO'),
        ('2102', 'PROVEEDORES DEL EXTERIOR', 'PASIVO'),
        ('2103', 'CUENTAS POR PAGAR A CORTO PLAZO', 'PASIVO'),
        ('210301', 'Cuentas por pagar a corto plazo', 'PASIVO'),
        ('210302', 'Acreedores varios a corto plazo', 'PASIVO'),
        ('210303', 'Pago a cuenta de impuesto sobre la renta', 'PASIVO'),
        ('2104', 'OBLIGACIONES BAJO ARRENDAMIENTO FINANCIERO CP', 'PASIVO'),
        ('2105', 'RETENCIONES LABORALES', 'PASIVO'),
        ('210501', 'ISSS Salud / Previsional', 'PASIVO'),
        ('210502', 'AFP Retención laboral', 'PASIVO'),
        ('210503', 'ISR - Retenciones a Empleados', 'PASIVO'),
        ('210504', 'ISR-Retenciones a Terceros', 'PASIVO'),
        ('2106', 'BENEFICIOS A EMPLEADOS POR PAGAR A CORTO PLAZO', 'PASIVO'),
        ('210601', 'ISSS-Salud (Patronal por pagar)', 'PASIVO'),
        ('210602', 'ISSS-Previsional (Patronal por pagar)', 'PASIVO'),
        ('210603', 'AFP Cuota Patronal', 'PASIVO'),
        ('210604', 'Sueldos y Salarios', 'PASIVO'),
        ('210605', 'Vacaciones', 'PASIVO'),
        ('210606', 'Aguinaldos', 'PASIVO'),
        ('210607', 'Indemnizaciones', 'PASIVO'),
        ('210608', 'Provisión para Prestaciones Laborales', 'PASIVO'),
        ('2107', 'SOBREGIROS Y PRÉSTAMOS BANCARIOS A CORTO PLAZO', 'PASIVO'),
        ('210701', 'Sobregiros Bancarios', 'PASIVO'),
        ('210702', 'Préstamos Bancarios', 'PASIVO'),
        ('210703', 'Porción circulante de préstamos a largo plazo', 'PASIVO'),
        ('2108', 'DIVIDENDOS POR PAGAR', 'PASIVO'),
        ('2109', 'PARTES RELACIONADAS POR PAGAR A CORTO PLAZO', 'PASIVO'),
        ('210901', 'Casa matriz', 'PASIVO'),
        ('210902', 'Sucursales', 'PASIVO'),
        ('210903', 'Accionistas', 'PASIVO'),
        ('210904', 'Directores y Ejecutivos', 'PASIVO'),
        ('210905', 'Subsidiarias', 'PASIVO'),
        ('210906', 'Asociadas', 'PASIVO'),
        ('2110', 'DEBITO FISCAL-IVA', 'PASIVO'),
        ('211001', 'Débito Fiscal por Ventas a Consumidor Final', 'PASIVO'),
        ('211002', 'Débito Fiscal por Ventas a Contribuyentes', 'PASIVO'),
        ('211003', 'Retención 1% IVA', 'PASIVO'),
        ('211004', 'Percepción 1% IVA', 'PASIVO'),
        ('211005', 'Retención 13% IVA', 'PASIVO'),
        ('2111', 'IMPUESTOS POR PAGAR', 'PASIVO'),
        ('211103', 'ISR-Pago a Cuenta', 'PASIVO'),
        ('211104', 'ISR - Diferido', 'PASIVO'),
        ('211105', 'Impuestos Municipales', 'PASIVO'),
        ('211106', 'IVA por Pagar', 'PASIVO'),
        ('2112', 'INGRESOS ANTICIPADOS', 'PASIVO'),
        ('22', 'PASIVO NO CORRIENTE', 'PASIVO'),
        ('2201', 'PRESTAMOS A LARGO PLAZO', 'PASIVO'),
        ('220101', 'Préstamos Bancarios LP', 'PASIVO'),
        ('2202', 'ACREEDORES COMERCIALES Y OTRAS CXP A LARGO PLAZO', 'PASIVO'),
        ('220201', 'Cuentas por pagar a largo plazo', 'PASIVO'),
        ('220202', 'Acreedores varios a largo plazo', 'PASIVO'),
        ('2203', 'OBLIGACIONES BAJO ARRENDAMIENTO FINANCIERO LP', 'PASIVO'),
        ('2204', 'PARTES RELACIONADAS POR PAGAR A LARGO PLAZO', 'PASIVO'),
        ('220401', 'Casa matriz LP', 'PASIVO'),
        ('220402', 'Sucursales LP', 'PASIVO'),
        ('220403', 'Accionistas LP', 'PASIVO'),
        ('220404', 'Directores y ejecutivos LP', 'PASIVO'),
        ('220405', 'Subsidiarias LP', 'PASIVO'),
        ('220406', 'Asociadas LP', 'PASIVO'),
        ('2205', 'BENEFICIOS A EMPLEADOS POR PAGAR A LARGO PLAZO', 'PASIVO'),
        ('220501', 'Indemnizaciones LP', 'PASIVO'),
        ('2206', 'ANTICIPOS Y GARANTIAS RECIBIDAS', 'PASIVO'),
        ('220601', 'Anticipos sobre ventas', 'PASIVO'),
        ('220602', 'Depósitos en garantia', 'PASIVO'),
        ('2207', 'PASIVO POR IMPUESTO DIFERIDO', 'PASIVO'),
        ('3', 'PATRIMONIO', 'PATRIMONIO'),
        ('31', 'PATRIMONIO NETO', 'PATRIMONIO'),
        ('3101', 'CAPITAL SOCIAL', 'PATRIMONIO'),
        ('310101', 'Capital Social Minimo', 'PATRIMONIO'),
        ('310102', 'Capital Social Variable', 'PATRIMONIO'),
        ('3102', 'RESERVA LEGAL', 'PATRIMONIO'),
        ('3103', 'RESERVA GENERAL', 'PATRIMONIO'),
        ('3104', 'SUPERÁVIT POR REVALUACIÓN', 'PATRIMONIO'),
        ('3105', 'RESULTADOS DE EJERCICIOS ANTERIORES', 'PATRIMONIO'),
        ('3106', 'RESULTADOS DEL EJERCICIO', 'PATRIMONIO'),
        ('310601', 'Utilidad del Ejercicio', 'PATRIMONIO'),
        ('310602', 'Pérdida del ejercicio (CR)', 'PATRIMONIO'),
        ('4', 'CUENTAS DE RESULTADO DEUDORAS', 'RESULTADO_DEUDORA'),
        ('41', 'COSTOS Y GASTOS DE OPERACIÓN', 'RESULTADO_DEUDORA'),
        ('4101', 'COSTOS DE VENTAS', 'RESULTADO_DEUDORA'),
        ('4102', 'COMPRAS', 'RESULTADO_DEUDORA'),
        ('410201', 'COMPRAS DE MERCANCIAS', 'RESULTADO_DEUDORA'),
        ('410202', 'GASTOS EN COMPRAS', 'RESULTADO_DEUDORA'),
        ('4103', 'REBAJAS Y DEVOLUCIONES SOBRE COMPRAS (CR)', 'RESULTADO_DEUDORA'),
        ('410301', 'Rebajas y Descuentos', 'RESULTADO_DEUDORA'),
        ('410302', 'Devoluciones', 'RESULTADO_DEUDORA'),
        ('4104', 'GASTOS DE ADMINISTRACIÓN', 'RESULTADO_DEUDORA'),
        ('410401', 'Sueldos y Salarios', 'RESULTADO_DEUDORA'),
        ('410402', 'Comisiones', 'RESULTADO_DEUDORA'),
        ('410403', 'Horas Extras', 'RESULTADO_DEUDORA'),
        ('410404', 'Aguinaldos', 'RESULTADO_DEUDORA'),
        ('410405', 'Vacaciones', 'RESULTADO_DEUDORA'),
        ('410406', 'Indemnizaciones', 'RESULTADO_DEUDORA'),
        ('410407', 'Bonificaciones y gratificaciones', 'RESULTADO_DEUDORA'),
        ('410408', 'Honorarios Profesionales', 'RESULTADO_DEUDORA'),
        ('410409', 'Dietas a Directores', 'RESULTADO_DEUDORA'),
        ('410410', 'Atenciones al personal', 'RESULTADO_DEUDORA'),
        ('410411', 'Atención a Junta Directiva Accionistas', 'RESULTADO_DEUDORA'),
        ('410412', 'Viáticos y transporte', 'RESULTADO_DEUDORA'),
        ('410413', 'ISSS Cuota Patronal', 'RESULTADO_DEUDORA'),
        ('410414', 'AFP Cuota Patronal', 'RESULTADO_DEUDORA'),
        ('410415', 'INSAFORP', 'RESULTADO_DEUDORA'),
        ('410416', 'Utensilios y enseres', 'RESULTADO_DEUDORA'),
        ('410417', 'Materiales Varios', 'RESULTADO_DEUDORA'),
        ('410418', 'Impuestos municipales', 'RESULTADO_DEUDORA'),
        ('410419', 'Papelería y Útiles', 'RESULTADO_DEUDORA'),
        ('410420', 'Servicio de agua', 'RESULTADO_DEUDORA'),
        ('410421', 'Energía eléctrica', 'RESULTADO_DEUDORA'),
        ('410422', 'Comunicaciones', 'RESULTADO_DEUDORA'),
        ('410423', 'Propaganda y anuncios', 'RESULTADO_DEUDORA'),
        ('410424', 'Encomiendas, envíos y fletes', 'RESULTADO_DEUDORA'),
        ('410425', 'Alquileres', 'RESULTADO_DEUDORA'),
        ('410426', 'Mantenimiento de local arrendado', 'RESULTADO_DEUDORA'),
        ('410427', 'Depreciación de edificaciones', 'RESULTADO_DEUDORA'),
        ('410428', 'Depreciación de mobiliario y equipo de oficina', 'RESULTADO_DEUDORA'),
        ('410429', 'Depreciación de equipo de transporte', 'RESULTADO_DEUDORA'),
        ('410430', 'Depreciación de maquinaria', 'RESULTADO_DEUDORA'),
        ('4105', 'GASTOS DE VENTA', 'RESULTADO_DEUDORA'),
        ('410501', 'Sueldos y salarios', 'RESULTADO_DEUDORA'),
        ('410502', 'Comisiones', 'RESULTADO_DEUDORA'),
        ('410503', 'Horas extras', 'RESULTADO_DEUDORA'),
        ('410504', 'Aguinaldos', 'RESULTADO_DEUDORA'),
        ('410505', 'Vacaciones', 'RESULTADO_DEUDORA'),
        ('410506', 'Indemnizaciones', 'RESULTADO_DEUDORA'),
        ('410507', 'Bonificaciones y gratificaciones', 'RESULTADO_DEUDORA'),
        ('410508', 'Horarios profesionales', 'RESULTADO_DEUDORA'),
        ('410509', 'Dietas a Directores', 'RESULTADO_DEUDORA'),
        ('410510', 'Atenciones al personal', 'RESULTADO_DEUDORA'),
        ('410511', 'Atención a Junta Directiva Accionistas', 'RESULTADO_DEUDORA'),
        ('410512', 'Viáticos y transporte', 'RESULTADO_DEUDORA'),
        ('410513', 'ISSS Cuota Patronal', 'RESULTADO_DEUDORA'),
        ('410514', 'AFP Cuota Patronal', 'RESULTADO_DEUDORA'),
        ('410515', 'INSAFORP', 'RESULTADO_DEUDORA'),
        ('410516', 'Utensilios y enseres', 'RESULTADO_DEUDORA'),
        ('410517', 'Materiales Varios', 'RESULTADO_DEUDORA'),
        ('410518', 'Impuestos municipales', 'RESULTADO_DEUDORA'),
        ('410519', 'Papelería y Útiles', 'RESULTADO_DEUDORA'),
        ('410529', 'Depreciación de equipo de transporte', 'RESULTADO_DEUDORA'),
        ('410530', 'Depreciación de maquinaria', 'RESULTADO_DEUDORA'),
        ('410531', 'Gastos no deducibles', 'RESULTADO_DEUDORA'),
        ('4106', 'GASTOS FINANCIEROS', 'RESULTADO_DEUDORA'),
        ('4107', 'OTROS GASTOS', 'RESULTADO_DEUDORA'),
        ('5', 'CUENTAS DE RESULTADO ACREEDORAS', 'RESULTADO_ACREEDORA'),
        ('51', 'INGRESOS DE OPERACIÓN', 'RESULTADO_ACREEDORA'),
        ('5101', 'VENTA DE MERCADERIA', 'RESULTADO_ACREEDORA'),
        ('510101', 'Ventas a consumidores finales', 'RESULTADO_ACREEDORA'),
        ('510102', 'Ventas a contribuyentes', 'RESULTADO_ACREEDORA'),
        ('510103', 'Exportaciones', 'RESULTADO_ACREEDORA'),
        ('5102', 'INGRESOS POR SERVICIOS', 'RESULTADO_ACREEDORA'),
        ('5103', 'REBAJAS Y DEVOLUCIONES SOBRE VENTAS (CR)', 'RESULTADO_ACREEDORA'),
        ('510301', 'Rebajas y Descuentos', 'RESULTADO_ACREEDORA'),
        ('510302', 'Devoluciones', 'RESULTADO_ACREEDORA'),
        ('52', 'INGRESOS NO DE OPERACIÓN', 'RESULTADO_ACREEDORA'),
        ('5201', 'OTROS INGRESOS', 'RESULTADO_ACREEDORA'),
        ('520101', 'Intereses', 'RESULTADO_ACREEDORA'),
        ('520102', 'Varios', 'RESULTADO_ACREEDORA'),
        ('6', 'CUENTAS LIQUIDADORAS', 'LIQUIDADORA'),
        ('61', 'CUENTAS LIQUIDADORAS DE RESULTADO', 'LIQUIDADORA'),
        ('6101', 'PÉRDIDAS Y GANANCIAS', 'LIQUIDADORA'),
        ('7', 'CUENTAS DE ORDEN', 'DE_ORDEN'),
        ('71', 'CUENTAS DE ORDEN DEUDORAS', 'DE_ORDEN'),
        ('7101', 'CUENTAS DE ORDEN', 'DE_ORDEN'),
        ('72', 'CUENTAS DE ORDEN ACREEDORAS', 'DE_ORDEN'),
        ('7201', 'CUENTAS DE ORDEN ACREEDORAS', 'DE_ORDEN');
        
        RAISE NOTICE 'Catálogo de cuentas insertado correctamente.';
    ELSE
        RAISE NOTICE 'El catálogo de cuentas ya contiene datos, omitiendo inserción.';
    END IF;
END $$;

-- Insertar cliente genérico (solo si no existen clientes)
INSERT INTO public.clientes (nombre, tipo_cliente, activo)
SELECT 'Cliente Contado', 'INDIVIDUAL', 'SI'
WHERE NOT EXISTS (SELECT 1 FROM public.clientes WHERE nombre = 'Cliente Contado');

-- Insertar productos de ejemplo (solo si no existen productos)
INSERT INTO public.productos_servicios (codigo, nombre, tipo, precio_unitario, unidad_medida, aplica_iva, activo)
SELECT * FROM (VALUES
    ('SERV-001', 'Servicio de Consultoría', 'SERVICIO', 50.00, 'Hora', 'SI', 'SI'),
    ('PROD-GEN', 'Producto Genérico', 'PRODUCTO', 10.00, 'Unidad', 'SI', 'SI')
) AS v(codigo, nombre, tipo, precio_unitario, unidad_medida, aplica_iva, activo)
WHERE NOT EXISTS (SELECT 1 FROM public.productos_servicios WHERE codigo = v.codigo);

-- =============================================
-- PASO 6: MIGRAR DATOS LEGACY DE FACTURAS (si existen)
-- =============================================

-- Migrar clientes únicos desde facturas legacy (con NIT)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM public.facturas WHERE cliente IS NOT NULL) THEN
        INSERT INTO public.clientes (nombre, nit, telefono, email, direccion, tipo_cliente, activo)
        SELECT DISTINCT ON (NULLIF(TRIM(nit_cliente), ''))
            COALESCE(NULLIF(TRIM(cliente), ''), 'Cliente Sin Nombre') AS nombre,
            NULLIF(TRIM(nit_cliente), '') AS nit,
            NULLIF(TRIM(telefono_cliente), '') AS telefono,
            NULLIF(TRIM(email_cliente), '') AS email,
            NULLIF(TRIM(direccion_cliente), '') AS direccion,
            CASE 
                WHEN LENGTH(NULLIF(TRIM(nit_cliente), '')) > 10 THEN 'EMPRESA'
                ELSE 'INDIVIDUAL'
            END AS tipo_cliente,
            'SI' AS activo
        FROM public.facturas
        WHERE nit_cliente IS NOT NULL 
            AND TRIM(nit_cliente) != ''
        ON CONFLICT (nit) DO NOTHING;

        -- Migrar clientes sin NIT
        INSERT INTO public.clientes (nombre, telefono, email, direccion, tipo_cliente, activo)
        SELECT DISTINCT ON (UPPER(TRIM(cliente)))
            NULLIF(TRIM(cliente), '') AS nombre,
            NULLIF(TRIM(telefono_cliente), '') AS telefono,
            NULLIF(TRIM(email_cliente), '') AS email,
            NULLIF(TRIM(direccion_cliente), '') AS direccion,
            'INDIVIDUAL' AS tipo_cliente,
            'SI' AS activo
        FROM public.facturas
        WHERE cliente IS NOT NULL 
            AND TRIM(cliente) != ''
            AND (nit_cliente IS NULL OR TRIM(nit_cliente) = '')
            AND NOT EXISTS (
                SELECT 1 FROM public.clientes c 
                WHERE UPPER(TRIM(c.nombre)) = UPPER(TRIM(facturas.cliente))
            )
        ORDER BY UPPER(TRIM(cliente)), fecha_emision DESC;

        -- Vincular facturas con clientes
        UPDATE public.facturas f
        SET id_cliente = c.id_cliente
        FROM public.clientes c
        WHERE f.id_cliente IS NULL
            AND f.nit_cliente IS NOT NULL 
            AND TRIM(f.nit_cliente) != ''
            AND TRIM(f.nit_cliente) = c.nit;

        UPDATE public.facturas f
        SET id_cliente = c.id_cliente
        FROM public.clientes c
        WHERE f.id_cliente IS NULL
            AND f.cliente IS NOT NULL
            AND TRIM(f.cliente) != ''
            AND UPPER(TRIM(f.cliente)) = UPPER(TRIM(c.nombre))
            AND c.nit IS NULL;

        RAISE NOTICE 'Migración de clientes completada.';
    END IF;
END $$;

-- Migrar productos/servicios desde facturas legacy
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM public.facturas WHERE producto_servicio IS NOT NULL) THEN
        INSERT INTO public.productos_servicios (codigo, nombre, descripcion, tipo, precio_unitario, unidad_medida, aplica_iva, activo)
        SELECT DISTINCT ON (UPPER(TRIM(producto_servicio)))
            'MIGR-' || LPAD(ROW_NUMBER() OVER (ORDER BY MIN(fecha_emision))::TEXT, 4, '0') AS codigo,
            NULLIF(TRIM(producto_servicio), '') AS nombre,
            'Producto/Servicio migrado desde facturas legacy el ' || CURRENT_DATE AS descripcion,
            CASE 
                WHEN LOWER(producto_servicio) LIKE '%servicio%' OR LOWER(producto_servicio) LIKE '%consultoría%' THEN 'SERVICIO'
                ELSE 'PRODUCTO'
            END AS tipo,
            COALESCE(AVG(subtotal), 100.00) AS precio_unitario,
            'Unidad' AS unidad_medida,
            CASE WHEN AVG(iva) > 0 THEN 'SI' ELSE 'NO' END AS aplica_iva,
            'SI' AS activo
        FROM public.facturas
        WHERE producto_servicio IS NOT NULL
            AND TRIM(producto_servicio) != ''
            AND NOT EXISTS (
                SELECT 1 FROM public.productos_servicios ps 
                WHERE UPPER(TRIM(ps.nombre)) = UPPER(TRIM(facturas.producto_servicio))
            )
        GROUP BY UPPER(TRIM(producto_servicio)), TRIM(producto_servicio)
        ORDER BY UPPER(TRIM(producto_servicio));

        RAISE NOTICE 'Migración de productos/servicios completada.';
    END IF;
END $$;

-- Migrar detalles de facturas legacy
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM public.facturas WHERE producto_servicio IS NOT NULL) THEN
        INSERT INTO public.factura_detalle (
            id_factura, id_producto, cantidad, precio_unitario, 
            descuento_porcentaje, descuento_monto, subtotal, iva, total_linea
        )
        SELECT 
            f.id_factura,
            COALESCE(ps.id_producto, (
                SELECT id_producto FROM public.productos_servicios 
                WHERE codigo = 'PROD-GEN' LIMIT 1
            )) AS id_producto,
            1.00 AS cantidad,
            CASE 
                WHEN f.descuento > 0 THEN f.subtotal + f.descuento
                ELSE f.subtotal
            END AS precio_unitario,
            0.00 AS descuento_porcentaje,
            f.descuento AS descuento_monto,
            f.subtotal,
            f.iva,
            f.monto_total
        FROM public.facturas f
        LEFT JOIN public.productos_servicios ps ON UPPER(TRIM(ps.nombre)) = UPPER(TRIM(f.producto_servicio))
        WHERE f.producto_servicio IS NOT NULL
            AND TRIM(f.producto_servicio) != ''
            AND NOT EXISTS (
                SELECT 1 FROM public.factura_detalle fd 
                WHERE fd.id_factura = f.id_factura
            );

        RAISE NOTICE 'Migración de detalles de factura completada.';
    END IF;
END $$;

-- =============================================
-- PASO 7: CREAR VISTAS ÚTILES
-- =============================================

-- Vista: Facturas completas con información del cliente
CREATE OR REPLACE VIEW v_facturas_completas AS
SELECT 
    f.id_factura,
    f.numero_factura,
    f.fecha_emision,
    f.fecha_vencimiento,
    COALESCE(c.nombre, f.cliente) AS cliente_nombre,
    COALESCE(c.nit, f.nit_cliente) AS cliente_nit,
    COALESCE(c.telefono, f.telefono_cliente) AS cliente_telefono,
    COALESCE(c.email, f.email_cliente) AS cliente_email,
    COALESCE(c.direccion, f.direccion_cliente) AS cliente_direccion,
    c.tipo_cliente,
    f.subtotal,
    f.descuento,
    f.iva,
    f.monto_total,
    f.condiciones_pago,
    f.vendedor,
    f.notas,
    CASE 
        WHEN f.id_cliente IS NOT NULL THEN 'NORMALIZADA'
        ELSE 'LEGACY'
    END AS tipo_factura
FROM public.facturas f
LEFT JOIN public.clientes c ON f.id_cliente = c.id_cliente;

-- Vista: Detalle de facturas con productos
CREATE OR REPLACE VIEW v_facturas_detalladas AS
SELECT 
    f.id_factura,
    f.numero_factura,
    f.fecha_emision,
    COALESCE(c.nombre, f.cliente) AS cliente_nombre,
    fd.id_detalle,
    ps.codigo AS producto_codigo,
    ps.nombre AS producto_nombre,
    ps.tipo AS producto_tipo,
    fd.cantidad,
    fd.precio_unitario,
    fd.descuento_porcentaje,
    fd.descuento_monto,
    fd.subtotal,
    fd.iva,
    fd.total_linea
FROM public.facturas f
LEFT JOIN public.clientes c ON f.id_cliente = c.id_cliente
INNER JOIN public.factura_detalle fd ON f.id_factura = fd.id_factura
INNER JOIN public.productos_servicios ps ON fd.id_producto = ps.id_producto;

-- Vista: Ventas por cliente
CREATE OR REPLACE VIEW v_ventas_por_cliente AS
SELECT 
    COALESCE(c.id_cliente, 0) AS id_cliente,
    COALESCE(c.nombre, f.cliente) AS cliente_nombre,
    c.tipo_cliente,
    COUNT(f.id_factura) AS total_facturas,
    SUM(f.monto_total) AS monto_total_vendido,
    AVG(f.monto_total) AS monto_promedio,
    MAX(f.fecha_emision) AS ultima_compra
FROM public.facturas f
LEFT JOIN public.clientes c ON f.id_cliente = c.id_cliente
GROUP BY c.id_cliente, c.nombre, f.cliente, c.tipo_cliente;

-- Vista: Productos más vendidos
CREATE OR REPLACE VIEW v_productos_mas_vendidos AS
SELECT 
    ps.id_producto,
    ps.codigo,
    ps.nombre,
    ps.tipo,
    ps.categoria,
    COUNT(DISTINCT fd.id_factura) AS num_facturas,
    SUM(fd.cantidad) AS cantidad_total_vendida,
    SUM(fd.total_linea) AS monto_total_vendido,
    AVG(fd.precio_unitario) AS precio_promedio
FROM public.productos_servicios ps
INNER JOIN public.factura_detalle fd ON ps.id_producto = fd.id_producto
GROUP BY ps.id_producto, ps.codigo, ps.nombre, ps.tipo, ps.categoria
ORDER BY cantidad_total_vendida DESC;

-- =============================================
-- PASO 8: CREAR FUNCIONES Y TRIGGERS
-- =============================================

-- Función: Actualizar fecha de actualización de clientes
CREATE OR REPLACE FUNCTION actualizar_fecha_cliente()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_ultima_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_fecha_cliente ON public.clientes;
CREATE TRIGGER trigger_actualizar_fecha_cliente
    BEFORE UPDATE ON public.clientes
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_cliente();

-- Función: Calcular totales de detalle de factura
CREATE OR REPLACE FUNCTION calcular_totales_detalle()
RETURNS TRIGGER AS $$
BEGIN
    NEW.subtotal = NEW.cantidad * NEW.precio_unitario;
    
    IF NEW.descuento_porcentaje > 0 THEN
        NEW.descuento_monto = NEW.subtotal * (NEW.descuento_porcentaje / 100);
    END IF;
    
    NEW.subtotal = NEW.subtotal - NEW.descuento_monto;
    
    IF EXISTS (
        SELECT 1 FROM public.productos_servicios ps 
        WHERE ps.id_producto = NEW.id_producto 
        AND ps.aplica_iva = 'SI'
    ) THEN
        NEW.iva = NEW.subtotal * 0.13;
    ELSE
        NEW.iva = 0.00;
    END IF;
    
    NEW.total_linea = NEW.subtotal + NEW.iva;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_calcular_totales_detalle ON public.factura_detalle;
CREATE TRIGGER trigger_calcular_totales_detalle
    BEFORE INSERT OR UPDATE ON public.factura_detalle
    FOR EACH ROW
    EXECUTE FUNCTION calcular_totales_detalle();

-- Función: Actualizar totales de factura desde detalles
CREATE OR REPLACE FUNCTION actualizar_totales_factura()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.facturas
    SET 
        subtotal = COALESCE((
            SELECT SUM(subtotal) FROM public.factura_detalle 
            WHERE id_factura = COALESCE(NEW.id_factura, OLD.id_factura)
        ), 0.00),
        iva = COALESCE((
            SELECT SUM(iva) FROM public.factura_detalle 
            WHERE id_factura = COALESCE(NEW.id_factura, OLD.id_factura)
        ), 0.00),
        monto_total = COALESCE((
            SELECT SUM(total_linea) FROM public.factura_detalle 
            WHERE id_factura = COALESCE(NEW.id_factura, OLD.id_factura)
        ), 0.00)
    WHERE id_factura = COALESCE(NEW.id_factura, OLD.id_factura);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_totales_factura_insert ON public.factura_detalle;
CREATE TRIGGER trigger_actualizar_totales_factura_insert
    AFTER INSERT OR UPDATE ON public.factura_detalle
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_totales_factura();

DROP TRIGGER IF EXISTS trigger_actualizar_totales_factura_delete ON public.factura_detalle;
CREATE TRIGGER trigger_actualizar_totales_factura_delete
    AFTER DELETE ON public.factura_detalle
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_totales_factura();

-- =============================================
-- PASO 9: MOSTRAR RESUMEN FINAL
-- =============================================

DO $$
DECLARE
    v_total_clientes INTEGER;
    v_total_productos INTEGER;
    v_total_facturas INTEGER;
    v_total_detalles INTEGER;
    v_total_cuentas INTEGER;
    v_total_transacciones INTEGER;
    v_facturas_normalizadas INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_total_clientes FROM public.clientes;
    SELECT COUNT(*) INTO v_total_productos FROM public.productos_servicios;
    SELECT COUNT(*) INTO v_total_facturas FROM public.facturas;
    SELECT COUNT(*) INTO v_total_detalles FROM public.factura_detalle;
    SELECT COUNT(*) INTO v_total_cuentas FROM public.catalogo_cuentas;
    SELECT COUNT(*) INTO v_total_transacciones FROM public.transacciones;
    SELECT COUNT(*) INTO v_facturas_normalizadas FROM public.facturas WHERE id_cliente IS NOT NULL;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'INICIALIZACIÓN Y MIGRACIÓN COMPLETADA';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'SISTEMA CONTABLE:';
    RAISE NOTICE '  - Catálogo de Cuentas: % cuentas', v_total_cuentas;
    RAISE NOTICE '  - Transacciones: %', v_total_transacciones;
    RAISE NOTICE '';
    RAISE NOTICE 'SISTEMA DE FACTURACIÓN:';
    RAISE NOTICE '  - Clientes: %', v_total_clientes;
    RAISE NOTICE '  - Productos/Servicios: %', v_total_productos;
    RAISE NOTICE '  - Facturas Totales: %', v_total_facturas;
    RAISE NOTICE '  - Facturas Normalizadas: %', v_facturas_normalizadas;
    RAISE NOTICE '  - Líneas de Detalle: %', v_total_detalles;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Base de datos lista para usar!';
    RAISE NOTICE '========================================';
END $$;

-- =============================================
-- FIN DEL SCRIPT
-- =============================================
