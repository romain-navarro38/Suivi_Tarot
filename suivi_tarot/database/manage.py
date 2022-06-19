import json
from pathlib import Path

from suivi_tarot.api.utils import CONFIG_FILE, COLOR_DEFAULT


def create_config_file():
    """Creation of the config.json file to store the database path
    and color list used for the game chart"""
    set_content_config_database({"path_database": "",
                                 "player_color": COLOR_DEFAULT})

def get_content_config_database() -> dict:
    """Retourne le contenu de config.json"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content: dict = json.load(f)
    return content

def set_content_config_database(content: dict):
    """Ecrit le dictionnaire content dans le fichier config.json"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=4)

def get_player_color_graph() -> list[str]:
    """Returns the list of colors used for the game chart"""
    return get_content_config_database().get("player_color")

def set_player_color_graph(default: bool, color_list: list = None):
    """Inserts in config.json the list of default colors if default is True
    otherwise the list passed as the second argument"""
    content = get_content_config_database()
    content["player_color"] = COLOR_DEFAULT if default else color_list
    set_content_config_database(content=content)

def check_presence_player_color_key() -> bool:
    """Returns true if the player_color key is present in config.json"""
    return "player_color" in get_content_config_database().keys()

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
    set_player_color_graph(default=False, color_list=['#696969', '#FF8C00', '#008000', '#FF0000', '#800080', '#800000'])
    print(get_player_color_graph())
