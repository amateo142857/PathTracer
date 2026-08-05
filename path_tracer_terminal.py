import os
import sys 
import time
import subprocess
import fnmatch 

def limpiar_pantalla():
    if os.name == "nt":  # Windows
        subprocess.run("cls", shell=True)
    else:  # Linux/Mac
        subprocess.run(["clear"])


def buscar_completo(directorio, patron, tipo="ambos", max_resultados=None):
    """
    Buscador completo con opciones
    
    Parámetros:
    - directorio: Ruta donde buscar
    - patron: Texto a buscar
    - tipo: "archivos", "carpetas", o "ambos"
    - max_resultados: Número máximo de resultados (None = sin límite)
    """
    resultados = {
        'archivos': [],
        'carpetas': [],
        'total': 0
    }
    
    contador = 0
    inicio = time.time()
    
    print(f"\n{'='*60}")
    print(f"🔍 BUSCANDO: '{patron}'")
    print(f"📂 Directorio: {directorio}")
    print(f"📌 Tipo: {tipo}")
    print(f"{'='*60}\n")
    
    for root, dirs, files in os.walk(directorio):
        if max_resultados and contador >= max_resultados:
            break
            
        # Buscar en carpetas
        if tipo in ["carpetas", "ambos"]:
            for carpeta in dirs:
                if max_resultados and contador >= max_resultados:
                    break
                    
                if patron.lower() in carpeta.lower():
                    ruta = os.path.join(root, carpeta)
                    resultados['carpetas'].append(ruta)
                    resultados['total'] += 1
                    contador += 1
                    print(f"  📁 {ruta}")
        
        # Buscar en archivos
        if tipo in ["archivos", "ambos"]:
            for archivo in files:
                if max_resultados and contador >= max_resultados:
                    break
                    
                if patron.lower() in archivo.lower():
                    ruta = os.path.join(root, archivo)
                    resultados['archivos'].append(ruta)
                    resultados['total'] += 1
                    contador += 1
                    print(f"  📄 {ruta}")
    
    fin = time.time()
    tiempo = fin - inicio
    
    print(f"\n{'='*60}")
    print(f"✅ RESULTADOS:")
    print(f"  📁 Carpetas: {len(resultados['carpetas'])}")
    print(f"  📄 Archivos: {len(resultados['archivos'])}")
    print(f"  📊 Total: {resultados['total']}")
    print(f"  ⏱️  Tiempo: {tiempo:.2f} segundos")
    print(f"{'='*60}\n")
    
    return resultados



def buscar_por_extension(directorio, extension):
    """Busca archivos con una extensión específica"""
    resultados = []
    
    # Asegurar que la extensión tenga punto
    if not extension.startswith('.'):
        extension = '.' + extension
    
    print(f"🔍 Buscando archivos *{extension} en {directorio}...")
    
    for root, dirs, files in os.walk(directorio):
        for archivo in files:
            if archivo.lower().endswith(extension.lower()):
                ruta_completa = os.path.join(root, archivo)
                resultados.append(ruta_completa)
                print(f"  📄 {archivo}")
    
    print(f"\n✅ Total encontrados: {len(resultados)}")
    input("\n\n Precione enter para continuar ...")
    return resultados



def buscar_por_nombre():
    directorio = input("📂 Directorio de búsqueda (Enter para actual): ").strip()
    if not directorio:
        directorio = '.'
    
    if not os.path.exists(directorio):
        print("❌ El directorio no existe")
        return
    
    patron = input("🔍 Patrón de búsqueda: ").strip()
    if not patron:
        print("❌ Debes ingresar un patrón")
        return
    max_res = input("📊 Máximo resultados (Enter para sin límite): ").strip()
    max_res = int(max_res) if max_res else None

    resultados = buscar_completo(directorio, patron, "ambos", max_res)
    input("Precione enter para continuar.....")


def buscar_con_comodines(directorio, patron, tipo="ambos"):
    
    resultados = []
    
    limpiar_pantalla()

    print(f"🔍 Buscando con comodín: '{patron}'")
    
    for root, dirs, files in os.walk(directorio):
        # Buscar en archivos
        if tipo in ["archivos", "ambos"]:
            for archivo in files:
                if fnmatch.fnmatch(archivo.lower(), patron.lower()):
                    ruta = os.path.join(root, archivo)
                    resultados.append(ruta)
                    print(f"  📄 {ruta}")
        
        # Buscar en carpetas
        if tipo in ["carpetas", "ambos"]:
            for carpeta in dirs:
                if fnmatch.fnmatch(carpeta.lower(), patron.lower()):
                    ruta = os.path.join(root, carpeta)
                    resultados.append(ruta)
                    print(f"  📁 {ruta}")
    
    print(f"\n✅ Total: {len(resultados)}")
    return resultados


def buscar_carpetas_por_nombre(directorio, patron):
    """Busca carpetas que contengan el patrón en el nombre"""
    resultados = []
    
    print(f"🔍 Buscando carpetas '{patron}' en {directorio}...")
    
    for root, dirs, files in os.walk(directorio):
        for carpeta in dirs:
            if patron.lower() in carpeta.lower():
                ruta_completa = os.path.join(root, carpeta)
                resultados.append(ruta_completa)
                print(f"  📁 Encontrado: {ruta_completa}")
    
    print(f"\n✅ Total carpetas encontradas: {len(resultados)}")
    return resultados


def buscar_archivos_por_nombre(directorio, patron, max_resultados=None):
    """
    Busca archivos que contengan el patrón en el nombre
    """
    resultados = []
    contador = 0
    
    print(f"🔍 Buscando '{patron}' en {directorio}...")
    
    for root, dirs, files in os.walk(directorio):
        if max_resultados and  contador >= max_resultados:
            break
            
        for archivo in files:
            if patron.lower() in archivo.lower():
                ruta_completa = os.path.join(root, archivo)
                resultados.append(ruta_completa)
                contador += 1
                print(f"  📄 Encontrado: {ruta_completa}")
                
                if max_resultados and contador >= max_resultados:
                    print(f"\n⚠️ Límite de {max_resultados} resultados alcanzado")
                    break
    
    print(f"\n✅ Total encontrados: {len(resultados)}")
    return resultados


def main():
    try:
        while True:
            limpiar_pantalla()

            print("\n" + "="*60)
            print("  🔍 BUSCADOR DE ARCHIVOS - VERSIÓN TERMINAL")
            print("="*60)
            print("  1. Buscar por nombre")
            print("  2. Buscar por extensión")
            print("  3. Buscar con comodines")
            print("  4. Buscar carpetas")
            print("  5. Buscar archivos")
            print("  6. Salir")
            print("="*60)

            opcion = input("\n👉 Selecciona una opción: ").strip()

            if opcion == '1':
                buscar_por_nombre()
            elif opcion == '2':
                directorio = input("📂 Directorio de búsqueda (Enter para actual): ").strip()
                if not directorio:
                    directorio = '.'

                if not os.path.exists(directorio):
                    print("❌ El directorio no existe")
                    return

                extension = input("🔍 Extensión (ej: .txt, .mp4): ").strip()
                if not extension.startswith('.'):
                    extension = '.' + extension

                resultados = buscar_por_extension(directorio, extension)

                if resultados:
                    print(f"\n✅ Encontrados: {len(resultados)} archivos")
            
            elif opcion == '3':
                directorio = input("📂 Directorio de búsqueda (Enter para actual): ").strip()
                if not directorio:
                    directorio = '.'

                if not os.path.exists(directorio):
                    print("❌ El directorio no existe")
                    return
                
                patron = input("🔍 Patrón (ej: *.txt, *proyecto*): ").strip()
                if not patron:
                    print("❌ Debes ingresar un patrón")
                    return

                tipo = input("📌 Tipo (archivos/carpetas/ambos): ").strip().lower()
                if tipo not in ['archivos', 'carpetas', 'ambos']:
                    tipo = 'ambos'

                buscar_con_comodines(directorio, patron, tipo)
                input("Precione enter para continuar ...")
            
            elif opcion == '4':
                directorio = input("📂 Directorio de búsqueda (Enter para actual): ").strip()
                if not directorio:
                    directorio = '.'

                if not os.path.exists(directorio):
                    print("❌ El directorio no existe")
                    return
                patron = input("🔍 Nombre de carpeta: ").strip()

                if not patron:
                    print("❌ Debes ingresar un nombre")
                    return
                
                buscar_carpetas_por_nombre(directorio, patron)
                input("Precione enter para continuar ...")
            elif opcion == '5':
                directorio = input("📂 Directorio de búsqueda (Enter para actual): ").strip()
                if not directorio:
                    directorio = '.'

                if not os.path.exists(directorio):
                    print("❌ El directorio no existe")
                    return
                patron = input("🔍 Nombre de archivo: ").strip()
                if not patron:
                    print("❌ Debes ingresar un nombre")
                    return
                
                max_res = input("📊 Máximo resultados (Enter para sin límite): ").strip()
                max_res = int(max_res) if max_res else None

                buscar_archivos_por_nombre(directorio, patron, max_res)
                input("Precione enter para continuar ...")
            elif opcion == '6':
                limpiar_pantalla()
                print("\n\nSaliedo del programa ....")
                sys.exit(1)
            else:
                print("❌ Opción inválida")
            

    except KeyboardInterrupt:
        print("\n\n Saliendo ....")


if __name__=='__main__':
    main()



