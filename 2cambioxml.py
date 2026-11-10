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
    arbol.write(ARCHIVO_XML, encoding='utf-8', xml_declaration=True)
    
    print(f"✅ Validación correcta. Se han grabado {len(filas)} registros en '{ARCHIVO_XML}'.")

except Exception as e:
    print(f"❌ ERROR EN LA GENERACIÓN DEL XML: {e}")
    sys.exit(1)