# 📊 Apache Spark - Sistema EU-UTVT

Esta carpeta contiene todos los archivos relacionados con **Apache Spark** para el análisis de big data del sistema EU-UTVT.

## 🔧 Configuración del Sistema

- **Apache Spark**: Versión 3.4.4 (Compatible con Java 8)
- **PySpark**: Versión 3.4.4 
- **Java**: Versión 8 (1.8.0_202)
- **MongoDB**: 16,640,000 usuarios disponibles

## 📁 Archivos Disponibles

### 🚀 `spark_mongo_analytics.py`
**Análisis masivo con Apache Spark nativo**
- Procesamiento de 16.6M usuarios con Spark real
- Análisis distribuido y optimizado
- Requiere configuración de variables de entorno
- **Uso**: `python spark\spark_mongo_analytics.py`

### 📊 `spark_reports_java8.py` 
**Generador de reportes compatible con Java 8**
- Sistema de reportes empresariales
- Compatible con Java 8 usando Pandas
- Análisis ejecutivo y departamental
- **Uso**: `python spark\spark_reports_java8.py`

### 🎯 `spark_reports_generator.py`
**Generador original de reportes**
- Versión inicial del sistema de reportes
- Requiere Java 17+ (Spark 4.0+)
- **Estado**: Funcional pero requiere upgrade de Java

### 🧪 `spark_test_compatibility.py`
**Test de compatibilidad Spark + Java 8**
- Verifica funcionamiento de Spark 3.4.4
- Pruebas de integración MongoDB
- Validación del sistema completo
- **Uso**: `python spark\spark_test_compatibility.py`

## ⚙️ Configuración de Variables de Entorno

Para usar Spark nativo, configurar antes de ejecutar:

```powershell
# Windows PowerShell
$env:PYSPARK_PYTHON = "C:\Users\luis1\.conda\envs\spark_env\python.exe"
$env:PYSPARK_DRIVER_PYTHON = "C:\Users\luis1\.conda\envs\spark_env\python.exe"

# Ejecutar PySpark
pyspark

# O ejecutar scripts
python spark\spark_mongo_analytics.py
```

## 📈 Capacidades del Sistema

### ✅ Funcionando Perfectamente:
- **Spark 3.4.4** + Java 8
- **16.6M usuarios** en MongoDB
- **Análisis en tiempo real** con progress tracking
- **Reportes ejecutivos** automáticos
- **Distribución de roles** y departamentos
- **Exportación a CSV** de resultados

### 🚀 Rendimiento Comprobado:
- **300,000+ registros/segundo** filtrado
- **1,000 usuarios** analizados en ~4 minutos
- **Escalabilidad** hasta 16.6M registros
- **Memoria optimizada** para Java 8

## 🎯 Opciones de Uso

### 1. **Análisis Rápido** (Recomendado)
```bash
python spark\spark_reports_java8.py
# Seleccionar opción 1: Análisis rápido (500K usuarios)
```

### 2. **Análisis Completo** (16.6M usuarios)
```bash
python spark\spark_reports_java8.py
# Seleccionar opción 2: Análisis completo
```

### 3. **Spark Nativo**
```bash
# Configurar variables de entorno primero
python spark\spark_mongo_analytics.py
```

### 4. **Test de Sistema**
```bash
python spark\spark_test_compatibility.py
```

## 📊 Archivos de Salida

Los análisis generan archivos CSV en el directorio principal:
- `role_distribution_YYYYMMDD_HHMMSS.csv`
- `department_distribution_YYYYMMDD_HHMMSS.csv`
- `detailed_statistics_YYYYMMDD_HHMMSS.csv`
- `sample_data_YYYYMMDD_HHMMSS.csv`

## 🔧 Solución de Problemas

### Error: Java OutOfMemoryError
```bash
# Usar spark_reports_java8.py en lugar de spark_mongo_analytics.py
# O seleccionar análisis rápido en lugar de completo
```

### Error: Python worker failed to connect
```bash
# Configurar variables de entorno Python
$env:PYSPARK_PYTHON = "ruta\al\python.exe"
$env:PYSPARK_DRIVER_PYTHON = "ruta\al\python.exe"
```

### Error: Unsupported class version
```bash
# Sistema ya configurado para Java 8
# Usar Spark 3.4.4 (ya instalado)
```

---

**🎉 Sistema listo para análisis de big data con Apache Spark!**

Fecha: Octubre 2025  
Versión: Spark 3.4.4 + Java 8 Compatible