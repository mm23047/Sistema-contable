-- =====================================================
-- SCRIPT DE CORRECCIÓN DE TIPOS DE CUENTA
-- Ejecutar en Query Tools de pgAdmin
-- Convierte tipos del catálogo contable estándar al formato del schema
-- =====================================================
-- 
-- ⚠️ NOTA IMPORTANTE:
-- Este script está incluido automáticamente en inicializacion_completa_bd.sql
-- Solo necesitas ejecutarlo manualmente si:
--   1. Tienes una base de datos antigua (creada antes de esta actualización)
--   2. Importaste datos desde otro sistema
--   3. Estás migrando desde una versión anterior del proyecto
-- 
-- Para instalaciones nuevas, simplemente ejecuta inicializacion_completa_bd.sql
-- =====================================================

-- Ver estado actual ANTES de la corrección
SELECT tipo_cuenta, COUNT(*) as cantidad
FROM public.catalogo_cuentas
GROUP BY tipo_cuenta
ORDER BY tipo_cuenta;

-- Actualizar tipos de cuenta al formato que espera el schema Pydantic
-- Mapeo:
--   ACTIVO → Activo
--   PASIVO → Pasivo
--   PATRIMONIO → Capital (equivalente contable)
--   RESULTADO_DEUDORA → Egreso (gastos/costos)
--   RESULTADO_ACREEDORA → Ingreso (ventas/ingresos)
--   LIQUIDADORA → Egreso (cuentas de cierre)
--   DE_ORDEN → Capital (cuentas memorándum)

UPDATE public.catalogo_cuentas
SET tipo_cuenta = CASE
    -- Conversión desde formato de catálogo contable
    WHEN tipo_cuenta = 'ACTIVO' THEN 'Activo'
    WHEN tipo_cuenta = 'PASIVO' THEN 'Pasivo'
    WHEN tipo_cuenta = 'PATRIMONIO' THEN 'Capital'
    WHEN tipo_cuenta = 'RESULTADO_DEUDORA' THEN 'Egreso'
    WHEN tipo_cuenta = 'RESULTADO_ACREEDORA' THEN 'Ingreso'
    WHEN tipo_cuenta = 'LIQUIDADORA' THEN 'Egreso'
    WHEN tipo_cuenta = 'DE_ORDEN' THEN 'Capital'
    
    -- Por si acaso ya están en formato correcto
    WHEN UPPER(tipo_cuenta) = 'ACTIVO' THEN 'Activo'
    WHEN UPPER(tipo_cuenta) = 'PASIVO' THEN 'Pasivo'
    WHEN UPPER(tipo_cuenta) = 'CAPITAL' THEN 'Capital'
    WHEN UPPER(tipo_cuenta) = 'INGRESO' THEN 'Ingreso'
    WHEN UPPER(tipo_cuenta) = 'EGRESO' THEN 'Egreso'
    
    ELSE tipo_cuenta
END;

-- Verificar resultado DESPUÉS de la corrección
SELECT tipo_cuenta, COUNT(*) as cantidad
FROM public.catalogo_cuentas
GROUP BY tipo_cuenta
ORDER BY tipo_cuenta;

-- Mostrar mensaje de confirmación con detalles
SELECT 
    '✅ Actualización completada exitosamente' as mensaje,
    COUNT(*) as total_cuentas,
    COUNT(CASE WHEN tipo_cuenta = 'Activo' THEN 1 END) as activos,
    COUNT(CASE WHEN tipo_cuenta = 'Pasivo' THEN 1 END) as pasivos,
    COUNT(CASE WHEN tipo_cuenta = 'Capital' THEN 1 END) as capital,
    COUNT(CASE WHEN tipo_cuenta = 'Ingreso' THEN 1 END) as ingresos,
    COUNT(CASE WHEN tipo_cuenta = 'Egreso' THEN 1 END) as egresos
FROM public.catalogo_cuentas;

-- Mostrar algunas cuentas de ejemplo para verificar
SELECT codigo_cuenta, nombre_cuenta, tipo_cuenta
FROM public.catalogo_cuentas
WHERE codigo_cuenta IN ('1', '2', '3', '4', '5', '6', '7')
ORDER BY codigo_cuenta;
