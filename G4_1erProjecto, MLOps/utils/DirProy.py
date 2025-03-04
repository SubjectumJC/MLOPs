import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto está en sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

def get_project_structure(root_dir=PROJECT_ROOT):
    """
    Recursively generates the structure of the project directory, excluding specified folders and file types.
    :param root_dir: The root directory of the project (default: PROJECT_ROOT).
    :return: A string representation of the directory structure.
    """
    excluded_dirs = {}

    def generate_structure(dir_path, prefix=""):
        try:
            entries = sorted(os.listdir(dir_path))
        except PermissionError:
            return ""  # Saltar directorios sin permiso de acceso
        structure = ""
        for index, entry in enumerate(entries):
            entry_path = os.path.join(dir_path, entry)
            is_last = (index == len(entries) - 1)
            connector = "└── " if is_last else "├── "

            # Excluir directorios y archivos .csv
            rel_path = os.path.relpath(entry_path, start=PROJECT_ROOT)
            if any(rel_path.startswith(excluded) for excluded in excluded_dirs) or entry.endswith('.csv'):
                continue

            structure += f"{prefix}{connector}{entry}/\n" if os.path.isdir(entry_path) else f"{prefix}{connector}{entry}\n"

            # Recursividad para subdirectorios
            if os.path.isdir(entry_path):
                extension = "    " if is_last else "│   "
                structure += generate_structure(entry_path, prefix + extension)
        return structure

    return generate_structure(root_dir)

if __name__ == "__main__":
    structure = get_project_structure()
    if structure:
        print(structure)
    else:
        print("No se encontraron directorios o archivos relevantes.")