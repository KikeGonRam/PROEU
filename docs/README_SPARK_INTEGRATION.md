# Integración Spark + MongoDB para 10M Usuarios - EU-UTVT

## 🎯 Sistema de Big Data Analytics

Este sistema integra **Apache Spark** con **MongoDB** para realizar análisis masivos de 10 millones de usuarios del sistema EU-UTVT.

## 📁 Archivos del Sistema

### 🔬 `spark_mongo_analytics.py` - Análisis Principal
**Motor de análisis principal con Spark + MongoDB**

**Características:**
- ✅ Conexión directa a MongoDB con 10M usuarios
- ✅ Carga optimizada de datos en lotes de 50K
- ✅ DataFrame Spark con schema optimizado
- ✅ Análisis básico y avanzado con Spark SQL
- ✅ Pruebas de rendimiento masivo
- ✅ Exportación de resultados

**Funcionalidades:**
1. **Análisis Básico**: Estadísticas generales, distribución por roles/departamentos
2. **Análisis Avanzado**: Consultas SQL complejas, análisis temporal, rankings
3. **Pruebas de Rendimiento**: Filtrado masivo, agregaciones, joins
4. **Exportación**: Resultados en CSV para análisis posterior

### 📊 `spark_reports_generator.py` - Generador de Reportes
**Sistema automatizado de reportes empresariales**

**Características:**
- ✅ Reportes ejecutivos automatizados
- ✅ Análisis departamental detallado
- ✅ Tendencias de actividad y retención
- ✅ Métricas de rendimiento del sistema
- ✅ Exportación en múltiples formatos

**Tipos de Reportes:**
1. **Ejecutivo**: Resumen de alto nivel para directivos
2. **Departamental**: Análisis detallado por cada departamento
3. **Tendencias**: Actividad temporal y patrones de uso
4. **Rendimiento**: Métricas del sistema y optimizaciones

## 🚀 Configuración del Entorno

### ✅ Tu configuración actual:
- **Spark 4.0.1** instalado en `C:\spark`
- **PySpark 4.0.1** en entorno `spark_env`
- **MongoDB Server** ejecutándose
- **PyMongo + Motor** para conectividad
- **Pandas + NumPy** para análisis complementario

### 🔧 Variables de entorno configuradas:
```bash
SPARK_HOME = C:\spark
PYSPARK_PYTHON = python (del entorno spark_env)
```

## 📊 Capacidades del Sistema

### 🎯 **Rendimiento Esperado:**

| Operación | 100K usuarios | 1M usuarios | 10M usuarios |
|-----------|---------------|-------------|--------------|
| Carga de datos | ~3 segundos | ~30 segundos | ~5 minutos |
| Filtrado simple | ~0.1 segundos | ~0.5 segundos | ~3 segundos |
| Agregación compleja | ~0.5 segundos | ~2 segundos | ~15 segundos |
| Join masivo | ~1 segundo | ~5 segundos | ~30 segundos |

### 📈 **Tipos de Análisis Disponibles:**

#### 🔍 **Análisis Básico:**
- Total de usuarios y tasa de actividad
- Distribución por roles (solicitante, aprobador, pagador, admin)
- Distribución por departamentos
- Estadísticas de login y actividad

#### 🧠 **Análisis Avanzado:**
- Análisis temporal de registros
- Actividad por departamento y rol cruzado
- Rankings de usuarios más activos
- Análisis de dominios de email
- Patrones de uso por día de la semana

#### 📊 **Análisis de Tendencias:**
- Crecimiento de usuarios por mes
- Retención de usuarios (última semana, mes, año)
- Actividad por día de la semana
- Análisis de cohortes

#### 🚀 **Análisis de Rendimiento:**
- Benchmarks de consultas
- Métricas de throughput
- Optimizaciones de cluster
- Recomendaciones de escalabilidad

## 🎮 Uso del Sistema

### 🚀 **Opción 1: Análisis Completo (Recomendado)**
```bash
# Activar entorno Spark
conda activate spark_env

# Ejecutar análisis principal
python spark_mongo_analytics.py
```

**Menú disponible:**
1. 📈 Análisis básico
2. 🔬 Análisis avanzado (Spark SQL)
3. 🚀 Pruebas de rendimiento
4. 💾 Exportar resultados
5. 🔄 Recargar datos

### 📋 **Opción 2: Generación de Reportes**
```bash
# Generar reportes empresariales
python spark_reports_generator.py
```

**Reportes disponibles:**
1. 📊 Reporte ejecutivo
2. 🏢 Reportes por departamento
3. 📈 Análisis de tendencias
4. 🚀 Reporte de rendimiento
5. 📑 Generar todos los reportes

## 📁 Estructura de Salida

### 📊 **Análisis Principal:**
```
spark_analysis_results/
├── role_distribution/          # Distribución por roles
├── department_distribution/    # Distribución por departamentos
└── detailed_statistics/        # Estadísticas detalladas
```

### 📋 **Reportes:**
```
reportes_departamentos_YYYYMMDD_HHMMSS/
├── reporte_Rectoría.txt
├── reporte_Sistemas_y_TI.txt
├── reporte_Finanzas.txt
└── ...

reporte_ejecutivo_YYYYMMDD_HHMMSS.txt
analisis_tendencias_YYYYMMDD_HHMMSS.txt
reporte_rendimiento_YYYYMMDD_HHMMSS.txt
```

## 🔧 Configuración Avanzada

### ⚡ **Optimización para 10M usuarios:**

**Configuración Spark en los scripts:**
```python
.config("spark.sql.adaptive.enabled", "true")
.config("spark.sql.adaptive.coalescePartitions.enabled", "true")
.config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
.config("spark.sql.execution.arrow.pyspark.enabled", "true")
.config("spark.driver.memory", "6g")
.config("spark.executor.memory", "4g")
```

**MongoDB optimizado:**
- Índices en campos críticos (email, role, department)
- Consultas por lotes de 50K registros
- Proyección de campos específicos

### 🎛️ **Personalización:**

**Modificar tamaños de lote:**
```python
# En spark_mongo_analytics.py línea 75
batch_size = 50000  # Cambiar según RAM disponible

# En los scripts de generación
BATCH_SIZE = 1000   # Para generación de usuarios
```

**Ajustar memoria Spark:**
```python
# Aumentar si tienes más RAM
.config("spark.driver.memory", "8g")
.config("spark.executor.memory", "6g")
```

## 📈 Consultas SQL Ejemplo

### 🔍 **Top usuarios por departamento:**
```sql
SELECT department, first_name, last_name, login_count,
       ROW_NUMBER() OVER (PARTITION BY department ORDER BY login_count DESC) as rank
FROM users 
WHERE login_count > 0
```

### 📊 **Análisis de actividad mensual:**
```sql
SELECT DATE_FORMAT(created_at, 'yyyy-MM') as month,
       COUNT(*) as new_users,
       SUM(COUNT(*)) OVER (ORDER BY DATE_FORMAT(created_at, 'yyyy-MM')) as cumulative
FROM users 
GROUP BY month
ORDER BY month
```

### 🏢 **Distribución departamento-rol:**
```sql
SELECT department, role, 
       COUNT(*) as total_users,
       AVG(login_count) as avg_activity,
       SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_users
FROM users 
GROUP BY department, role
ORDER BY total_users DESC
```

## 🛠️ Troubleshooting

### ❌ **Error: Java no encontrado**
```bash
# Instalar Java 8 o 11
# Verificar JAVA_HOME
echo $env:JAVA_HOME
```

### ❌ **Error: Memoria insuficiente**
```python
# Reducir configuración de memoria
.config("spark.driver.memory", "2g")
.config("spark.executor.memory", "2g")
```

### ❌ **Error: MongoDB connection**
```bash
# Verificar servicio MongoDB
Get-Service | Where-Object {$_.Name -like "*mongo*"}
```

### ⚠️ **Performance lento:**
1. Aumentar `spark.default.parallelism`
2. Usar más particiones: `df.repartition(200)`
3. Cachear DataFrames frecuentes: `df.cache()`

## 🎯 Casos de Uso Empresariales

### 👨‍💼 **Para Directivos:**
- Reportes ejecutivos automatizados
- Métricas de adopción del sistema
- Análisis de departamentos más activos
- ROI del sistema de solicitudes

### 👩‍💻 **Para Administradores TI:**
- Métricas de rendimiento del sistema
- Análisis de carga por departamento
- Identificación de usuarios inactivos
- Optimización de recursos

### 📊 **Para Analistas:**
- Análisis de tendencias de uso
- Segmentación de usuarios
- Análisis de retención
- Predicción de crecimiento

## 🚀 Escalabilidad

**El sistema está diseñado para escalar:**
- ✅ **10M usuarios actuales**
- ✅ **50M usuarios** (con más RAM)
- ✅ **100M usuarios** (cluster distribuido)
- ✅ **Integración con Hadoop/HDFS**
- ✅ **Streaming analytics** con Spark Streaming

## 📞 Soporte

Para optimizaciones específicas o escalamiento del cluster:
1. Ajustar configuración de memoria según hardware
2. Configurar cluster Spark distribuido para datasets > 50M
3. Implementar particionamiento por fecha/departamento
4. Integrar con herramientas de visualización (Tableau, Power BI)

¡El sistema está listo para analizar 10 millones de usuarios con Apache Spark! 🚀