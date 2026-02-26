# Informe de Cobertura de Calidad del Dato

**Dominio / Coleccion**: [DOMINIO]
**Scope**: [Dominio completo / Tabla(s): NOMBRE]
**Fecha de generacion**: [YYYY-MM-DD]
**Agente**: Data Quality Expert

---

## Resumen Ejecutivo

| Metrica | Valor |
|---------|-------|
| Tablas analizadas | N |
| Reglas existentes | N |
| Estado OK | N |
| Estado KO | N |
| Estado WARNING | N |
| Sin ejecutar | N |
| **Cobertura estimada** | **XX%** |
| Gaps criticos | N |
| Gaps moderados | N |
| Gaps bajos | N |
| Reglas creadas esta sesion | N |

---

## Cobertura por Tabla

| Tabla | Completeness | Uniqueness | Validity | Consistency | Otras (Timeliness, etc.) | Cobertura |
|-------|-------------|------------|----------|-------------|-------------------------|-----------|
| [tabla] | OK/Gap/Parcial | OK/Gap/Parcial | OK/Gap/Parcial | OK/Gap/N/A | OK/Gap/N/A | XX% |

**Nota sobre Dimensiones**: Las dimensiones mostradas pueden variar segun las definiciones especificas del dominio. La definicion del dominio prevalece sobre la estandar en caso de ambiguedad.

**Leyenda:**
- **OK**: dimension cubierta y regla pasando
- **Parcial**: hay regla pero no cubre todas las columnas relevantes
- **Gap**: no existe regla donde deberia haberla
- **N/A**: dimension no aplica a esta tabla
- **KO**: hay regla pero esta fallando

---

## Detalle de Reglas Existentes

### [Nombre de Tabla]

| Regla | Dimension | Estado | % Pass | Descripcion |
|-------|-----------|--------|--------|-------------|
| [nombre-regla] | completeness | OK | 100.0% | [descripcion] |
| **[nombre-regla-ko]** | validity | **KO** | 42.3% | [descripcion] |

---

## Gaps Identificados

| Prioridad | Tabla | Columna | Dimension | Descripcion |
|-----------|-------|---------|-----------|-------------|
| CRITICO | [tabla] | [columna] | uniqueness | Clave primaria sin verificacion de unicidad |
| ALTO | [tabla] | [columna] | completeness | Campo obligatorio de negocio sin verificacion de nulos |
| MEDIO | [tabla] | [columna] | validity | Importe sin verificacion de rango valido |

---

## Reglas Creadas en Esta Sesion

| Regla | Tabla | Dimension | Estado |
|-------|-------|-----------|--------|
| [nombre-regla] | [tabla] | [dimension] | created |

---

## Recomendaciones y Proximos Pasos

1. [Recomendacion 1]
2. [Recomendacion 2]
3. [Recomendacion 3]

---

*Generado por Data Quality Agent*
