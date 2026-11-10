import xml.etree.ElementTree as ET
from collections import Counter
import re
import json
import webbrowser
import os

# ==============================================================================
# CONFIGURACIÓN: Cambia aquí el nombre de tu nuevo archivo XML
# ==============================================================================
ARCHIVO_XML = "incidencies.xml"      # Ejemplo: Pon aquí 'mis_4000_respuestas.xml'
ARCHIVO_HTML_SALIDA = "dashboard_4000.html"

def generar_dashboard_html(fitxer_xml, fitxer_sortida):
    if not os.path.exists(fitxer_xml):
        print(f"❌ Error: No se encuentra el archivo '{fitxer_xml}'. Revisa el nombre.")
        return

    print(f"⏳ Cargando y procesando '{fitxer_xml}'...")
    
    # 1. Cargar el XML
    tree = ET.parse(fitxer_xml)
    root = tree.getroot()
    registres = root.findall('incidencia')
    total_rebuts = len(registres)

    valides = []
    erronies = []
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    # 2. Limpieza de datos (Data Cleaning)
    for inc in registres:
        data_str = inc.findtext('Fecha_de_la_incidencia', '')
        email = inc.findtext('Correo_electrónico', '')
        descripcio = inc.findtext('Descripción_detallada', '')
        ubicacio = inc.findtext('Ubicación_de_la_incidencia', '')
        categoria = inc.findtext('Categoría_del_fallo', '')
        
        motius = []
        any_inc = None
        if '/' in data_str:
            parts = data_str.split('/')
            if len(parts) >= 3:
                try:
                    any_inc = int(parts[2].split(' ')[0])
                except ValueError:
                    pass
        
        if any_inc is not None and (any_inc < 2010 or any_inc > 2026):
            motius.append("Año fuera de rango")
        if email and not re.match(email_regex, email):
            motius.append("Email no válido")
        if ubicacio.lower() == 'dummy' or categoria.lower() == 'dummy':
            motius.append("Dummy/Test")
        if len(descripcio.strip()) < 4 or descripcio.strip().lower() in ['no se', 'ns', 'a', 'test']:
            motius.append("Sin información")
        elif len(descripcio) > 800:
            motius.append("Spam/Texto largo")

        if motius:
            erronies.append(inc)
        else:
            valides.append(inc)

    total_valides = len(valides)
    total_erronies = len(erronies)

    # 3. Agrupaciones estadísticas (Escalado a Top 10 para grandes volúmenes de datos)
    eq_data = Counter([i.findtext('Tipo_de_equipamiento', 'N/A') for i in valides]).most_common(10)
    ub_data = Counter([i.findtext('Ubicación_de_la_incidencia', 'N/A') for i in valides]).most_common(10)
    cat_data = Counter([i.findtext('Categoría_del_fallo', 'N/A') for i in valides]).most_common(10)
    imp_data = Counter([i.findtext('Nivel_de_impacto', 'N/A') for i in valides]).most_common(5)

    # Conversión segura a formato JSON para JavaScript
    eq_labels, eq_values = json.dumps([x[0] for x in eq_data]), json.dumps([x[1] for x in eq_data])
    ub_labels, ub_values = json.dumps([x[0] for x in ub_data]), json.dumps([x[1] for x in ub_data])
    cat_labels, cat_values = json.dumps([x[0] for x in cat_data]), json.dumps([x[1] for x in cat_data])
    imp_labels, imp_values = json.dumps([x[0].split('/')[0].strip() for x in imp_data]), json.dumps([x[1] for x in imp_data])

    # 4. Generación de la plantilla HTML interactiva
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Incidencias ({total_rebuts} Respuestas)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --primary: #2563eb;
            --text-color: #1e293b;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 25px;
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            color: #0f172a;
        }}
        .kpi-container {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}
        .kpi-card {{
            background: var(--card-bg);
            padding: 15px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            text-align: center;
            min-width: 180px;
        }}
        .kpi-card .num {{
            font-size: 28px;
            font-weight: bold;
            color: var(--primary);
        }}
        .kpi-card .label {{
            font-size: 13px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
            max-width: 1300px;
            margin: 0 auto;
        }}
        .card {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .card h3 {{
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 16px;
            color: #334155;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
        }}
        .chart-container {{
            position: relative;
            height: 320px;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Dashboard de Incidencias</h1>
        <p>Análisis interactivo de <strong>{total_rebuts}</strong> respuestas recibidas en ({fitxer_xml})</p>
    </div>

    <div class="kpi-container">
        <div class="kpi-card">
            <div class="num">{total_rebuts}</div>
            <div class="label">Total Respuestas</div>
        </div>
        <div class="kpi-card">
            <div class="num" style="color: #16a34a;">{total_valides}</div>
            <div class="label">Válidas ({ (total_valides/total_rebuts)*100:.1f}% )</div>
        </div>
        <div class="kpi-card">
            <div class="num" style="color: #dc2626;">{total_erronies}</div>
            <div class="label">Filtradas / Ruido ({ (total_erronies/total_rebuts)*100:.1f}% )</div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>🖥️ Top Equipamiento Afectado</h3>
            <div class="chart-container"><canvas id="chartEquip"></canvas></div>
        </div>

        <div class="card">
            <h3>📍 Top 10 Ubicaciones con Más Incidencias</h3>
            <div class="chart-container"><canvas id="chartUbic"></canvas></div>
        </div>

        <div class="card">
            <h3>⚠️ Categorías de Fallo Principal</h3>
            <div class="chart-container"><canvas id="chartCat"></canvas></div>
        </div>

        <div class="card">
            <h3>⚡ Niveles de Impacto Operativo</h3>
            <div class="chart-container"><canvas id="chartImp"></canvas></div>
        </div>
    </div>

    <script>
        const eqLabels = {eq_labels};
        const eqValues = {eq_values};

        const ubLabels = {ub_labels};
        const ubValues = {ub_values};

        const catLabels = {cat_labels};
        const catValues = {cat_values};

        const impLabels = {imp_labels};
        const impValues = {imp_values};

        // Gráfico 1: Equipamiento
        new Chart(document.getElementById('chartEquip'), {{
            type: 'bar',
            data: {{
                labels: eqLabels,
                datasets: [{{
                    label: 'Incidencias',
                    data: eqValues,
                    backgroundColor: '#3b82f6',
                    borderRadius: 6
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});

        // Gráfico 2: Ubicaciones (Horizontal)
        new Chart(document.getElementById('chartUbic'), {{
            type: 'bar',
            data: {{
                labels: ubLabels,
                datasets: [{{
                    label: 'Incidencias',
                    data: ubValues,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }}]
            }},
            options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});

        // Gráfico 3: Categoría Fallo (Horizontal)
        new Chart(document.getElementById('chartCat'), {{
            type: 'bar',
            data: {{
                labels: catLabels,
                datasets: [{{
                    label: 'Incidencias',
                    data: catValues,
                    backgroundColor: '#f59e0b',
                    borderRadius: 6
                }}]
            }},
            options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});

        // Gráfico 4: Impacto (Doughnut)
        new Chart(document.getElementById('chartImp'), {{
            type: 'doughnut',
            data: {{
                labels: impLabels,
                datasets: [{{
                    data: impValues,
                    backgroundColor: ['#f97316', '#eab308', '#ef4444', '#8b5cf6', '#06b6d4']
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
    </script>
</body>
</html>"""

    with open(fitxer_sortida, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Dashboard generado exitosamente en '{fitxer_sortida}'")
    
    # Abre el archivo en el navegador por defecto (Windows, Mac o Linux)
    webbrowser.open('file://' + os.path.realpath(fitxer_sortida))

if __name__ == '__main__':
    generar_dashboard_html(ARCHIVO_XML, ARCHIVO_HTML_SALIDA)