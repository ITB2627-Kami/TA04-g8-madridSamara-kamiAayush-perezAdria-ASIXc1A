import csv
import xml.etree.ElementTree as ET
import os
import sys

ARCHIVO_CSV = 'incidencies.csv'
ARCHIVO_XML = 'incidencies.xml'

print("⏳ Validando la estructura y formato del archivo CSV...\n")

# 1. Comprobar existencia del archivo
if not os.path.exists(ARCHIVO_CSV):
    print("❌ ERROR DE FICHERO:")
    print(f"   No se encuentra el archivo '{ARCHIVO_CSV}' en la carpeta actual.")
    sys.exit(1)

# 2. Lectura y validación estricta de formato CSV y UTF-8
filas = []
try:
    with open(ARCHIVO_CSV, mode='r', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        filas = list(lector)
        
        # Validar si el CSV carece de estructura de columnas
        if not lector.fieldnames:
            print("❌ ERROR DE FORMATO CSV:")
            print("   El archivo CSV no contiene un encabezado válido.")
            sys.exit(1)

except UnicodeDecodeError as e:
    print("❌ ERROR DE FORMATO DE ARCHIVO (UnicodeDecodeError):")
    print(f"   Detalle del byte no válido: {e}")
    print("   Causa: El CSV generado desde el PDF contiene una codificación de caracteres dañada o no compatible con UTF-8.")
    print("   Resultado: Se ha cancelado la conversión a XML para evitar corrupción de datos.")
    sys.exit(1)

except csv.Error as e:
    print("❌ ERROR DE ESTRUCTURA EN CSV:")
    print(f"   Error de sintaxis CSV: {e}")
    print("   Resultado: El archivo está mal delimitado o corrupto.")
    sys.exit(1)

except Exception as e:
    print(f"❌ ERROR INESPERADO AL LER EL CSV: {e}")
    sys.exit(1)

# 2.5 Nueva comprobación: Verificar si el XML de destino ya existe
destino_xml = ARCHIVO_XML

if os.path.exists(ARCHIVO_XML):
    print(f"⚠️  AVISO DE FICHERO EXISTENTE:")
    print(f"   El archivo '{ARCHIVO_XML}' ya existe en esta carpeta.")
    
    while True:
        opcion = input("   ¿Qué deseas hacer? [S]obreescribir / [N]uevo archivo / [C]ancelar: ").strip().lower()
        
        if opcion in ('s', 'sobreescribir'):
            break
            
        elif opcion in ('n', 'nuevo'):
            # Generar sugerencia automática libre (ej. incidencies_1.xml)
            base, ext = os.path.splitext(ARCHIVO_XML)
            contador = 1
            while os.path.exists(f"{base}_{contador}{ext}"):
                contador += 1
            sugerencia = f"{base}_{contador}{ext}"
            
            nuevo_nombre = input(f"   Introduce el nuevo nombre (pulsa Enter para usar '{sugerencia}'): ").strip()
            
            if not nuevo_nombre:
                destino_xml = sugerencia
                break
            else:
                if not nuevo_nombre.lower().endswith('.xml'):
                    nuevo_nombre += '.xml'
                if os.path.exists(nuevo_nombre):
                    print(f"   ❌ El archivo '{nuevo_nombre}' también existe. Elige otro nombre.\n")
                    continue
                destino_xml = nuevo_nombre
                break
                
        elif opcion in ('c', 'cancelar'):
            print("\n🛑 Operación cancelada por el usuario. No se ha modificado ningún archivo.")
            sys.exit(0)
            
        else:
            print("   ⚠️ Opción no válida. Escribe 'S' para sobreescribir, 'N' para crear uno nuevo o 'C' para cancelar.\n")

# 3. Conversión a XML (solo si la validación ha sido 100% correcta)
try:
    raiz = ET.Element('incidencies')
    
    for fila in filas:
        incidencia = ET.SubElement(raiz, 'incidencia')
        for clave, valor in fila.items():
            if clave is None:
                continue
            nombre_etiqueta = clave.strip().replace(' ', '_').replace('/', '_')
            campo = ET.SubElement(incidencia, nombre_etiqueta)
            campo.text = str(valor) if valor is not None else ""

    arbol = ET.ElementTree(raiz)
    arbol.write(destino_xml, encoding='utf-8', xml_declaration=True)
    
    print(f"\n✅ Validación correcta. Se han grabado {len(filas)} registros en '{destino_xml}'.")

except Exception as e:
    print(f"❌ ERROR EN LA GENERACIÓN DEL XML: {e}")
    sys.exit(1)