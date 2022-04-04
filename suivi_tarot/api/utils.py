from pathlib import Path
from random import choice

CUR_FILE = Path(__file__)
DATA_FOLDER = CUR_FILE.parent.parent.parent
DATA_FILE = DATA_FOLDER / "db.sqlite3"
IMAGE_FOLDER = CUR_FILE.parent.parent / "ressource" / "image"

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

TETE = ["R \u2665",  # cœur
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


if __name__ == "__main__":
    print(get_random_item_with_constraint(PLAYERS, "Romain"))
