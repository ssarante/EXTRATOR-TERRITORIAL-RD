import camelot
import pandas as pd
import json
import sys

sys.setrecursionlimit(3000)  # aumenta límite de recursión

def extract_and_save_tables(file_path, output_name, flavor='lattice'):
    all_dfs = []
    try:
        print("Iniciando extracción de tablas...")

        # Número total de páginas manual
        total_pages = 519  # reemplaza con el número real si cambia
        print(f"PDF tiene {total_pages} páginas.")

        # Procesar página por página
        for page in range(1, total_pages + 1):
            print(f"Procesando página {page}...")
            tables = camelot.read_pdf(file_path, flavor=flavor, pages=str(page))
            print(f"  Se encontraron {tables.n} tablas en esta página.")
            if tables.n > 0:
                all_dfs.extend([table.df for table in tables])

        if not all_dfs:
            print("No se encontraron tablas en el PDF.")
            return

        combined_df = pd.concat(all_dfs, ignore_index=True)
        print("Todas las tablas se combinaron en un único DataFrame.")

        # Guardar CSV
        csv_file_path = f"{output_name}.csv"
        combined_df.to_csv(csv_file_path, index=False, header=False, encoding='utf-8-sig')
        print(f"Datos guardados en CSV: {csv_file_path}")

        # Guardar JSON
        json_file_path = f"{output_name}.json"
        json_data = combined_df.to_dict(orient='records')
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"Datos guardados en JSON: {json_file_path}")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

# --- Ejecución ---
pdf_file = 'division-territorial-2021.pdf'
output_base_name = 'extracted_data'
extract_and_save_tables(pdf_file, output_base_name, flavor='stream')
