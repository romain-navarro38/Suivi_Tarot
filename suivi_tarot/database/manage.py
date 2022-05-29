import json
from pathlib import Path

from suivi_tarot.api.utils import CONFIG_FILE


def create_config_file():
    """Création au niveau du projet du fichier config.json
    stockant le chemin de la base de données"""
    set_content_config_database({"path_database": ""})

def get_content_config_database() -> dict:
    """Retourne le contenu de config.json"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content: dict = json.load(f)
    return content

def set_content_config_database(content: dict):
    """Ecrit le dictionnaire content dans le fichier config.json"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=4)

def get_path_database(extension: str) -> tuple[Path, bool]:
    """Retourne le chemin et sa validée de la base de données
    stocké dans config.json"""
    content = get_content_config_database()
    path = Path(content.get("path_database"))
    valid = path_database_is_valid(path, extension)
    return path, valid

def add_path_database(path: str):
    """Ajoute le chemin de la base de données à config.json"""
    content = get_content_config_database()
    content["path_database"] = path
    set_content_config_database(content=content)

def path_database_is_valid(path: Path, extension: str) -> bool:
    """Retourne la validité d'un chemin de fichier"""
    return path.is_file() and path.suffix == extension


if __name__ == "__main__":
    print(CONFIG_FILE.exists())
    db, is_valid = get_path_database(".sqlite3")
    print(is_valid)
