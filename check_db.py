from pymongo import MongoClient
from collections import Counter

# Conectar directamente con valores por defecto
client = MongoClient('mongodb://localhost:27017')
db = client['sistema_solicitudes_pagos']

# Verificar solicitudes
solicitudes = list(db['solicitudes_estandar'].find())
print(f'═══════════════════════════════════════════════════════════════════')
print(f'SOLICITUDES EN BASE DE DATOS')
print(f'═══════════════════════════════════════════════════════════════════')
print(f'Total solicitudes: {len(solicitudes)}\n')

if solicitudes:
    from collections import Counter
    estados = Counter([s.get('estado', 'sin_estado') for s in solicitudes])
    print('📊 RESUMEN DE ESTADOS:')
    for estado, count in estados.items():
        emoji = '✅' if estado in ['enviada', 'en_revision'] else '📋'
        print(f'  {emoji} {estado}: {count}')
    
    print(f'\n📝 DETALLE DE CADA SOLICITUD:')
    print('-' * 100)
    for i, sol in enumerate(solicitudes, 1):
        estado = sol.get('estado', 'sin_estado')
        departamento = sol.get('departamento', 'N/A')
        monto = sol.get('monto', 0)
        moneda = sol.get('tipo_moneda', 'N/A')
        beneficiario = sol.get('nombre_beneficiario', 'N/A')
        fecha = sol.get('fecha_creacion', 'N/A')
        
        print(f'{i}. ID: {str(sol["_id"])}')
        print(f'   Estado: {estado} | Depto: {departamento} | Monto: ${monto:,.2f} {moneda}')
        print(f'   Beneficiario: {beneficiario}')
        print(f'   Fecha creación: {fecha}')
        print()
    
    # Contar cuántas están disponibles para el aprobador
    disponibles = sum(1 for s in solicitudes if s.get('estado') in ['enviada', 'en_revision'])
    print(f'\n🎯 SOLICITUDES DISPONIBLES PARA APROBADOR:')
    print(f'   {disponibles} de {len(solicitudes)} solicitudes están en estado "enviada" o "en_revision"')
    
    if disponibles == 0:
        print(f'\n⚠️  PROBLEMA IDENTIFICADO:')
        print(f'   Ninguna solicitud está en estado "enviada" o "en_revision"')
        print(f'   El dashboard del aprobador solo muestra solicitudes en estos estados.')
        print(f'\n💡 SOLUCIÓN:')
        print(f'   Para cambiar el estado de una solicitud, puedes:')
        print(f'   1. Usar MongoDB Compass para editar manualmente el campo "estado" a "enviada"')
        print(f'   2. O crear una nueva solicitud desde el dashboard del solicitante')
else:
    print('⚠️  No hay solicitudes en la base de datos')
    print('   Para probar el dashboard del aprobador:')
    print('   1. Inicia sesión como SOLICITANTE')
    print('   2. Crea una nueva solicitud')
    print('   3. Envíala (cambiará a estado "enviada")')
    print('   4. Luego inicia sesión como APROBADOR')

print(f'\n═══════════════════════════════════════')
print(f'USUARIOS EN BASE DE DATOS')
print(f'═══════════════════════════════════════')

# Verificar usuarios
users = list(db['users'].find({}, {'email': 1, 'first_name': 1, 'last_name': 1, 'role': 1, '_id': 0}))
print(f'Total usuarios: {len(users)}\n')

if users:
    print('Usuarios registrados:')
    for u in users:
        email = u.get('email', 'N/A')
        nombre = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
        role = u.get('role', 'N/A')
        print(f'  - {email:<30} | {nombre:<25} | Role: {role}')
        
    roles = Counter([u.get('role', 'sin_role') for u in users])
    print('\nRoles disponibles:')
    for role, count in roles.items():
        print(f'  - {role}: {count}')
else:
    print('⚠️  No hay usuarios en la base de datos')

print(f'\n═══════════════════════════════════════')
