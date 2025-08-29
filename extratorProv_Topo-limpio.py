import camelot
import pandas as pd
import json
import sys
from PyPDF2 import PdfReader
import re

sys.setrecursionlimit(3000)

def get_total_pages(file_path):
    reader = PdfReader(file_path)
    return len(reader.pages)

def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    # quitar espacios extra
    name = name.strip()
    # poner título estándar (Primera letra mayúscula)
    name = name.title()
    return name

def extract_and_save_tables(file_path, output_name, flavor='lattice'):
    all_dfs = []
    try:
        print("Iniciando extracción de tablas...")

        total_pages = get_total_pages(file_path)
        print(f"PDF tiene {total_pages} páginas.")

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

        # --- quedarnos solo con Provincia (col 1) y Toponimia (col 7) ---
        filtered_df = combined_df.iloc[:, [1, 7]]
        filtered_df.columns = ["Provincia", "Toponimia"]

        # --- limpiar datos ---
        filtered_df["Provincia"] = filtered_df["Provincia"].astype(str).str.strip()
        filtered_df["Toponimia"] = filtered_df["Toponimia"].astype(str).apply(normalize_name)

        # --- filtrar basura ---
        blacklist = [
            "Provincia", "Municipio", "Distrito", "Sección", "Zona Urbana",
            "Nacional", "Capitanía", "General", "Ley", "Fecha", "Local", "Ubicación geográfica"
            , "Extensión territorial", "Población", "Antecedentes históricos", "No. Ley", "Unidad territorial", "Cuenta con las siguientes áreas:"
            , "Relieve:", "Recursos mineros:", "Hidrografía:", "Clima:", "Áreas protegidas:", "Reserva científica:"
        ]
        pattern = re.compile("|".join(blacklist), re.IGNORECASE)

        filtered_df = filtered_df[
            ~filtered_df["Toponimia"].str.contains(pattern, na=False)
        ]

        # --- quitar duplicados ignorando mayúsculas/minúsculas ---
        filtered_df = (
            filtered_df
            .drop_duplicates(subset=["Provincia", "Toponimia"], keep="first")
            .reset_index(drop=True)
        )

        print("Se filtraron Provincia + Toponimia, normalizados y sin duplicados/basura.")

        # Guardar CSV
        csv_file_path = f"{output_name}.csv"
        filtered_df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
        print(f"Datos guardados en CSV: {csv_file_path}")

        # Guardar JSON
        json_file_path = f"{output_name}.json"
        json_data = filtered_df.to_dict(orient='records')
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"Datos guardados en JSON: {json_file_path}")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


# --- Ejecución ---
pdf_file = 'division-territorial-2021.pdf'
output_base_name = 'provincias_toponimia_limpio'
extract_and_save_tables(pdf_file, output_base_name, flavor='stream')
