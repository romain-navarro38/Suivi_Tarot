import hashlib
import uuid
from pathlib import Path
from random import choice

CUR_FILE = Path(__file__)
ROOT_FOLDER = CUR_FILE.parent.parent.parent
DATA_FILE = ROOT_FOLDER / "db.sqlite3"
CONFIG_FILE = ROOT_FOLDER / "config.json"
IMAGE_FOLDER = ROOT_FOLDER / "ressource" / "image"

HEADER_3_4 = ["Preneur",
              "Contrat",
              "Bout",
              "Point",
              "Poignée",
              "Petit au bout",
              "Petit Chelem",
              "Grand Chelem"]

HEADER_5 = ["Preneur",
            "Contrat",
            "Bout",
            "Point",
            "Tête",
            "Appelé",
            "Poignée",
            "Petit au bout",
            "Petit Chelem",
            "Grand Chelem"]

HEADER_6 = ["PNJ",
            "Preneur",
            "Contrat",
            "Bout",
            "Point",
            "Tête",
            "Appelé",
            "Poignée",
            "Petit au bout",
            "Petit Chelem",
            "Grand Chelem"]

HEAD = ["R \u2665",  # cœur
        "R \u2666",  # carreau
        "R \u2663",  # trefle
        "R \u2660",  # pique
        "D \u2665",
        "D \u2666",
        "D \u2663",
        "D \u2660"]

PLAYERS = ["Romain", "Ludo", "Emeline", "Eddy", "Aurore"]

COLOR_GRAPH = ['blue', 'darkorange', 'green', 'red', 'purple', 'maroon']


def get_random_item_with_constraint(list_str: list[str], prohibited_item: str) -> str:
    # sourcery skip: use-assigned-variable
    """Retourne un élément choisi aléatoirement dans une liste de str
    avec la contrainte d'être différent d'un élément en particulier"""
    item = prohibited_item
    while prohibited_item == item:
        item = choice(list_str)
    return item


def generate_salt() -> str:
    """Retourne une chaîne de caractères unique"""
    return str(uuid.uuid4())


def hashage_password(password: str, salt: str = "") -> tuple[str, str]:
    """Génére le hash d'une chaîne de caractères en lui ajoutant un sel.
    Retourne le hash et le sel utilisé"""
    if not salt:
        salt = generate_salt()
    hash_ = hashlib.sha256(bytes((password + salt).encode('utf-8'))).hexdigest()
    return hash_, salt


def move_database(path: str):
    """Déplace la base de données créée dans le dossier projet vers le dossier
    sélectionné par l'utilisateur"""
    DATA_FILE.rename(Path(path) / DATA_FILE.name)


if __name__ == "__main__":
    print(hashage_password("romain"))
