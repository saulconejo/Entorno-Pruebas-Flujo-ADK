import os
import shutil
from pathlib import Path

def clean_null_bytes_from_directory(directory_path):
    """Limpia bytes nulos de todos los archivos .py en un directorio"""
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"El directorio {directory_path} no existe")
        return
    
    print(f"Verificando archivos en: {directory}")
    files_with_nulls = []
    files_cleaned = []
    
    # Buscar todos los archivos .py
    for py_file in directory.rglob("*.py"):
        try:
            # Leer archivo en modo binario
            with open(py_file, 'rb') as f:
                content = f.read()
            
            # Verificar si contiene bytes nulos
            if b'\x00' in content:
                files_with_nulls.append(py_file)
                print(f"❌ Bytes nulos encontrados en: {py_file}")
                
                # Crear backup
                backup_path = py_file.with_suffix('.py.backup')
                shutil.copy2(py_file, backup_path)
                print(f"   Backup creado: {backup_path}")
                
                # Limpiar bytes nulos
                clean_content = content.replace(b'\x00', b'')
                
                # Escribir archivo limpio
                with open(py_file, 'wb') as f:
                    f.write(clean_content)
                
                files_cleaned.append(py_file)
                print(f"✅ Archivo limpiado: {py_file}")
            else:
                print(f"✅ Archivo OK: {py_file}")
                
        except Exception as e:
            print(f"❌ Error procesando {py_file}: {e}")
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN:")
    print(f"Archivos con bytes nulos encontrados: {len(files_with_nulls)}")
    print(f"Archivos limpiados: {len(files_cleaned)}")
    
    if files_cleaned:
        print("\nArchivos limpiados:")
        for file in files_cleaned:
            print(f"  - {file}")
        print("\nBackups creados con extensión .backup")
    
    return len(files_with_nulls) == 0

def verify_encoding(directory_path):
    """Verifica la codificación de los archivos"""
    directory = Path(directory_path)
    
    for py_file in directory.rglob("*.py"):
        try:
            # Intentar leer como UTF-8
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Codificación UTF-8 OK: {py_file}")
        except UnicodeDecodeError as e:
            print(f"❌ Error de codificación en {py_file}: {e}")
            
            # Intentar leer con diferentes codificaciones
            encodings = ['latin-1', 'windows-1252', 'cp1252']
            for encoding in encodings:
                try:
                    with open(py_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # Reescribir como UTF-8
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Recodificado de {encoding} a UTF-8: {py_file}")
                    break
                except:
                    continue
        except Exception as e:
            print(f"❌ Error leyendo {py_file}: {e}")

if __name__ == "__main__":
    # Cambiar esta ruta por la ruta a tu módulo
    module_path = "multi_tool_agent"
    
    print("PASO 1: Limpiando bytes nulos...")
    clean_success = clean_null_bytes_from_directory(module_path)
    
    print("\nPASO 2: Verificando codificación...")
    verify_encoding(module_path)
    
    print("\n" + "="*50)
    if clean_success:
        print("✅ LISTO: Todos los archivos están limpios")
        print("Ahora puedes ejecutar: adk run .\\multi_tool_agent\\")
    else:
        print("⚠️  Se encontraron y limpiaron archivos con problemas")
        print("Intenta ejecutar de nuevo: adk run .\\multi_tool_agent\\")