#!/usr/bin/env python3
"""
Script para corregir las rutas de archivos en la base de datos.
Convierte rutas completas como 'uploads/solicitudes/filename.pdf' a solo 'filename.pdf'
"""

from pymongo import MongoClient
from app.config.settings import settings

def fix_file_paths():
    """Corregir rutas de archivos en la base de datos"""
    
    # Conectar a MongoDB
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    collection = db["solicitudes_estandar"]
    
    try:
        # Buscar todas las solicitudes que tengan archivos adjuntos
        solicitudes = list(collection.find({"archivos_adjuntos": {"$exists": True, "$ne": []}}))
        
        print(f"Encontradas {len(solicitudes)} solicitudes con archivos adjuntos")
        
        updated_count = 0
        
        for solicitud in solicitudes:
            archivos_actualizados = []
            actualizar = False
            
            for archivo in solicitud.get("archivos_adjuntos", []):
                ruta_actual = archivo.get("ruta_archivo", "")
                print(f"Ruta actual: '{ruta_actual}'")
                
                # Si la ruta contiene 'uploads' y 'solicitudes', extraer solo el nombre del archivo
                if ("uploads" in ruta_actual and "solicitudes" in ruta_actual) or "/" in ruta_actual or "\\" in ruta_actual:
                    # Extraer solo el nombre del archivo usando os.path.basename
                    import os
                    nuevo_nombre = os.path.basename(ruta_actual)
                    if nuevo_nombre != ruta_actual:
                        archivo["ruta_archivo"] = nuevo_nombre
                        actualizar = True
                        print(f"Corrigiendo: {ruta_actual} -> {nuevo_nombre}")
                    else:
                        print(f"No necesita corrección: {ruta_actual}")
                else:
                    print(f"No necesita corrección: {ruta_actual}")
                
                archivos_actualizados.append(archivo)
            
            # Si hay cambios, actualizar la solicitud
            if actualizar:
                collection.update_one(
                    {"_id": solicitud["_id"]},
                    {"$set": {"archivos_adjuntos": archivos_actualizados}}
                )
                updated_count += 1
                print(f"Actualizada solicitud ID: {solicitud['_id']}")
        
        print(f"\nProceso completado:")
        print(f"- Solicitudes revisadas: {len(solicitudes)}")
        print(f"- Solicitudes actualizadas: {updated_count}")
        
    except Exception as e:
        print(f"Error durante la corrección: {e}")
    
    finally:
        # Cerrar conexión
        client.close()

if __name__ == "__main__":
    print("Iniciando corrección de rutas de archivos...")
    fix_file_paths()
    print("Corrección completada.")