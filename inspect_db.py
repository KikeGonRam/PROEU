#!/usr/bin/env python3
"""
Script para inspeccionar las rutas de archivos en la base de datos.
"""

from pymongo import MongoClient
from app.config.settings import settings
import json

def inspect_file_paths():
    """Inspeccionar rutas de archivos en la base de datos"""
    
    # Conectar a MongoDB
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    collection = db["solicitudes_estandar"]
    
    try:
        # Buscar todas las solicitudes que tengan archivos adjuntos
        solicitudes = list(collection.find({"archivos_adjuntos": {"$exists": True, "$ne": []}}))
        
        print(f"Encontradas {len(solicitudes)} solicitudes con archivos adjuntos")
        
        for i, solicitud in enumerate(solicitudes):
            print(f"\n=== Solicitud {i+1} (ID: {solicitud['_id']}) ===")
            
            archivos = solicitud.get("archivos_adjuntos", [])
            print(f"Archivos adjuntos: {len(archivos)}")
            
            for j, archivo in enumerate(archivos):
                print(f"  Archivo {j+1}:")
                print(f"    - Nombre: {archivo.get('nombre_archivo', 'N/A')}")
                print(f"    - Ruta: '{archivo.get('ruta_archivo', 'N/A')}'")
                print(f"    - Tipo: {archivo.get('tipo_archivo', 'N/A')}")
                print(f"    - Tamaño: {archivo.get('tamaño', 'N/A')} bytes")
        
    except Exception as e:
        print(f"Error durante la inspección: {e}")
    
    finally:
        # Cerrar conexión
        client.close()

if __name__ == "__main__":
    print("Inspeccionando rutas de archivos en la base de datos...")
    inspect_file_paths()
    print("\nInspección completada.")