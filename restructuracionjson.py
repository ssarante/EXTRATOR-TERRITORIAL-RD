import csv
import json

# Función para normalizar los nombres de columna
def normalize_headers(headers):
    return [h.strip().upper() for h in headers]

# Cargar provincias
provincias = {}
with open('codigo_provincia.csv', newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    reader.fieldnames = normalize_headers(reader.fieldnames)  # normalizar headers
    for row in reader:
        codigo_str = row.get('CODIGO_PROVINCIA', '').strip()
        nombre = row.get('NOMBRE_PROVINCIA', '').strip()
        if not codigo_str or not nombre:
            continue  # ignorar filas vacías o incompletas
        try:
            codigo = int(codigo_str)
        except ValueError:
            continue
        provincias[codigo] = {
            "codigo": codigo,
            "nombre_provincia": nombre,
            "sectores": []
        }

# Agregar sectores a cada provincia
with open('provincias_toponimia_limpio1.csv', newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    reader.fieldnames = normalize_headers(reader.fieldnames)
    for row in reader:
        codigo_str = row.get('CODIGO_PROVINCIA', '').strip()
        sector = row.get('TOPONIMIA_NOMBRE', '').strip()
        if not codigo_str or not sector:
            continue  # ignorar filas vacías
        try:
            codigo = int(codigo_str)
        except ValueError:
            continue
        if codigo in provincias:
            provincias[codigo]["sectores"].append(sector)

# Convertir a lista y guardar JSON
resultado = list(provincias.values())

with open('provincias_con_sectores.json', 'w', encoding='utf-8') as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print("JSON generado correctamente en provincias_con_sectores.json")
