# Generador Masivo de Usuarios - EU-UTVT

Este directorio contiene scripts para generar 10 millones de usuarios de prueba para el sistema EU-UTVT.

## Scripts Disponibles

### 1. `generate_massive_users.py` - Versión Estándar
- **Propósito**: Generación completa con todos los campos de usuario
- **Velocidad**: ~1,000-2,000 usuarios/segundo
- **Memoria**: Uso moderado
- **Características**:
  - Datos completos y realistas usando Faker
  - Validación completa de datos
  - Estadísticas detalladas
  - Manejo robusto de errores

### 2. `generate_users_optimized.py` - Versión Optimizada
- **Propósito**: Generación rápida usando multiprocesamiento
- **Velocidad**: ~5,000-10,000 usuarios/segundo
- **Memoria**: Uso optimizado
- **Características**:
  - Procesamiento paralelo con múltiples workers
  - Configuración optimizada de MongoDB
  - Inserción en lotes grandes
  - Creación de índices diferida

## Requisitos Previos

```bash
pip install motor faker bcrypt
```

## Configuración de MongoDB

Antes de ejecutar los scripts, asegúrate de que MongoDB esté optimizado:

```javascript
// Configuración recomendada en MongoDB
use eu_utvt_db

// Aumentar cache size si es posible
db.adminCommand({setParameter: 1, wiredTigerCacheSizeGB: 4})

// Configurar journaling para escrituras masivas
db.adminCommand({setParameter: 1, syncdelay: 300})
```

## Uso

### Generación Estándar (Recomendada para desarrollo)
```bash
python generate_massive_users.py
```

### Generación Optimizada (Recomendada para producción)
```bash
python generate_users_optimized.py
```

## Configuración Personalizable

Puedes modificar estas variables en los scripts:

```python
TOTAL_USERS = 10_000_000    # Número total de usuarios
BATCH_SIZE = 5000           # Usuarios por lote
MAX_WORKERS = 8             # Workers paralelos (solo versión optimizada)
```

## Estructura de Datos Generados

Cada usuario incluye:

```json
{
  "user_id": 1,
  "email": "user1@utvt.edu.mx",
  "password": "hashed_password",
  "first_name": "Juan",
  "last_name": "Pérez",
  "department": "Sistemas y TI",
  "role": "solicitante",
  "phone": "+52 55 123 4567",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "profile": {
    "employee_id": "EMP00000001",
    "position": "Analista de Sistemas"
  },
  "metadata": {
    "generated_at": "2024-10-02T15:45:00",
    "batch_id": 1
  }
}
```

## Distribución de Roles

- **70% Solicitantes** (7,000,000 usuarios)
- **20% Aprobadores** (2,000,000 usuarios)  
- **8% Pagadores** (800,000 usuarios)
- **2% Administradores** (200,000 usuarios)

## Departamentos Incluidos

- Rectoría
- Dirección Académica
- Dirección Administrativa
- Finanzas
- Recursos Humanos
- Sistemas y TI
- Mantenimiento
- Biblioteca
- Servicios Escolares
- Vinculación
- Investigación
- Y más...

## Rendimiento Esperado

### Hardware Recomendado
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Almacenamiento**: SSD recomendado
- **MongoDB**: Configuración optimizada

### Tiempos Estimados

| Usuarios | Versión Estándar | Versión Optimizada |
|----------|------------------|-------------------|
| 100K     | ~2 minutos       | ~30 segundos      |
| 1M       | ~20 minutos      | ~3 minutos        |
| 10M      | ~3 horas         | ~30 minutos       |

## Monitoreo

Durante la ejecución verás:

```
🚀 Iniciando generación paralela de usuarios...
📊 Total: 10,000,000 | Lotes: 5,000 | Workers: 8
📈 Worker 0: 500,000 usuarios | 8,500/seg
📈 Worker 1: 450,000 usuarios | 8,200/seg
...
✅ GENERACIÓN COMPLETADA
⏱️ Tiempo total: 28.5 minutos
🚀 Velocidad: 5,847 usuarios/segundo
```

## Verificación de Datos

Ambos scripts incluyen funciones de verificación:

```bash
# Verificar datos después de la generación
python -c "
import asyncio
from generate_users_optimized import quick_verify
asyncio.run(quick_verify())
"
```

## Limpieza y Mantenimiento

### Limpiar datos de prueba
```javascript
// En MongoDB
use eu_utvt_db
db.users.deleteMany({"metadata.source": "massive_generation"})
```

### Optimizar después de inserción masiva
```javascript
// Compactar colección
db.runCommand({compact: "users"})

// Rehacer estadísticas
db.users.reIndex()
```

## Solución de Problemas

### Error: Conexión a MongoDB
```bash
# Verificar que MongoDB esté corriendo
mongod --version
systemctl status mongod
```

### Error: Memoria insuficiente
- Reducir `BATCH_SIZE` a 1000-2000
- Reducir `MAX_WORKERS` a 2-4
- Aumentar swap del sistema

### Error: Índices únicos
```javascript
// Limpiar índices duplicados
db.users.dropIndex("email_1")
db.users.createIndex({"email": 1}, {"unique": true})
```

## Comandos Útiles

### Consultas de análisis
```javascript
// Contar por rol
db.users.aggregate([
  {$group: {_id: "$role", count: {$sum: 1}}},
  {$sort: {count: -1}}
])

// Usuarios por departamento
db.users.aggregate([
  {$group: {_id: "$department", count: {$sum: 1}}},
  {$sort: {count: -1}}
])

// Estadísticas de creación
db.users.aggregate([
  {$group: {
    _id: {$dateToString: {format: "%Y-%m", date: "$created_at"}},
    count: {$sum: 1}
  }},
  {$sort: {_id: 1}}
])
```

### Exportar muestra
```bash
# Exportar 1000 usuarios de muestra
mongoexport --db=eu_utvt_db --collection=users --limit=1000 --out=sample_users.json
```

## Notas Importantes

1. **Backup**: Haz respaldo antes de ejecutar en producción
2. **Espacio**: 10M usuarios requieren ~2-3GB de espacio
3. **Índices**: Se crean automáticamente al final
4. **Passwords**: Todos usan "password123" hasheado para testing
5. **IDs únicos**: Cada usuario tiene user_id secuencial único

## Integración con Sistema

Los usuarios generados son compatibles con:
- Sistema de autenticación JWT
- Roles y permisos existentes  
- Flujo de solicitudes
- Reportes y estadísticas

¡Listo para generar 10 millones de usuarios! 🚀