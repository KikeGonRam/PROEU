# Tests - Sistema de Solicitudes de Pagos

Este directorio contiene los archivos de prueba del sistema.

## Archivos de Test

### `test_auth.py`
- **Propósito**: Prueba la autenticación con diferentes métodos (bcrypt directo vs passlib)
- **Uso**: `python tests/test_auth.py`
- **Descripción**: Diagnostica problemas de compatibilidad entre diferentes librerías de hash

### `test_controller.py` 
- **Propósito**: Prueba el controlador de usuarios y la autenticación completa
- **Uso**: `python tests/test_controller.py`
- **Descripción**: Verifica que el controlador UserController funcione correctamente

## Cómo ejecutar los tests

```bash
# Desde el directorio raíz del proyecto
python tests/test_auth.py
python tests/test_controller.py
```

## Notas

- Los tests requieren que MongoDB esté ejecutándose
- Los tests requieren que la base de datos esté inicializada con `python init_db.py`
- Los tests son principalmente para diagnóstico y desarrollo, no para producción