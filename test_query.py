from pymongo import MongoClient

# Conectar a la base de datos
client = MongoClient('mongodb://localhost:27017')
db = client['sistema_solicitudes_pagos']
solicitudes_collection = db["solicitudes_estandar"]

# Esta es EXACTAMENTE la query que usa el controlador
query = {
    "estado": {
        "$in": ["enviada", "en_revision"]
    }
}

print("═══════════════════════════════════════════════════════════════════")
print("PROBANDO LA QUERY DEL CONTROLADOR")
print("═══════════════════════════════════════════════════════════════════")
print(f"Query: {query}\n")

# Ejecutar la query
solicitudes = list(solicitudes_collection.find(query).sort("fecha_creacion", -1))

print(f"✅ Resultados encontrados: {len(solicitudes)}\n")

if solicitudes:
    print("📝 SOLICITUDES QUE DEBE MOSTRAR EL DASHBOARD:")
    print("-" * 100)
    for i, sol in enumerate(solicitudes, 1):
        print(f"{i}. ID: {str(sol['_id'])}")
        print(f"   Estado: {sol.get('estado')}")
        print(f"   Departamento: {sol.get('departamento')}")
        print(f"   Monto: ${sol.get('monto', 0):,.2f} {sol.get('tipo_moneda', 'N/A')}")
        print(f"   Beneficiario: {sol.get('nombre_beneficiario', 'N/A')}")
        print(f"   Solicitante Email: {sol.get('solicitante_email', 'N/A')}")
        print()
else:
    print("❌ No se encontraron solicitudes con esta query")
    print("   Esto explicaría por qué el dashboard está vacío")

print("═══════════════════════════════════════════════════════════════════")
