import csv
import xml.etree.ElementTree as ET

# Abre el CSV leyendo correctamente todos los caracteres (UTF-8)
with open('incidencies.csv', mode='r', encoding='utf-8') as f:
    lector = csv.DictReader(f)
    
    # Elemento raíz del XML
    raiz = ET.Element('incidencies')
    
    for fila in lector:
        incidencia = ET.SubElement(raiz, 'incidencia')
        for clave, valor in fila.items():
            # Reemplaza espacios en los nombres de columna para que sean etiquetas válidas
            nombre_etiqueta = clave.strip().replace(' ', '_').replace('/', '_')
            campo = ET.SubElement(incidencia, nombre_etiqueta)
            campo.text = valor

# Guarda el resultado en incidencies.xml
arbol = ET.ElementTree(raiz)
arbol.write('incidencies.xml', encoding='utf-8', xml_declaration=True)
