from pathlib import Path

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
