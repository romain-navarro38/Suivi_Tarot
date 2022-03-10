from pathlib import Path

CUR_FILE = Path(__file__)
DATA_FOLDER = CUR_FILE.parent.parent.parent
DATA_FILE = DATA_FOLDER / "db.sqlite3"
IMAGE_FOLDER = CUR_FILE.parent.parent / "ressource" / "image"

EN_TETE_3_4 = ["Preneur",
               "Contrat",
               "Bout",
               "Point",
               "Poignée",
               "Petit au bout",
               "Pt Chelem",
               "Gr Chelem"]

EN_TETE_5 = ["Preneur",
             "Contrat",
             "Bout",
             "Point",
             "Tête",
             "Appelé",
             "Poignée",
             "Petit au bout",
             "Pt Chelem",
             "Gr Chelem"]

EN_TETE_6 = ["PNJ",
             "Preneur",
             "Contrat",
             "Bout",
             "Point",
             "Tête",
             "Appelé",
             "Poignée",
             "Petit au bout",
             "Pt Chelem",
             "Gr Chelem"]

TETE = ["R \u2665",  # cœur
        "R \u2666",  # carreau
        "R \u2663",  # trefle
        "R \u2660",  # pique
        "D \u2665",
        "D \u2666",
        "D \u2663",
        "D \u2660"]

JOUEURS = ["Romain", "Ludo", "Emeline", "Eddy", "Aurore"]

COLOR_GRAPH = ['blue', 'darkorange', 'green', 'red', 'purple', 'maroon']

T_JOUEUR = """
    CREATE TABLE joueur (
    id INTEGER NOT NULL UNIQUE,
    pseudo TEXT NOT NULL UNIQUE,
    nom TEXT,
    prenom TEXT,
    actif INTEGER NOT NULL CHECK(actif IN (0, 1)),
    protege INTEGER NOT NULL CHECK(protege IN (0, 1)),
    PRIMARY KEY(id AUTOINCREMENT)
);"""

T_SESSION = """
CREATE TABLE session (
    id INTEGER NOT NULL UNIQUE,
    date_ TEXT NOT NULL UNIQUE,
    table_ INTEGER NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT)
);"""

T_SESSION_JOUEUR = """
CREATE TABLE session_joueur (
    id INTEGER NOT NULL UNIQUE,
    session INTEGER NOT NULL,
    joueur INTEGER NOT NULL,
    FOREIGN KEY(session) REFERENCES session(id),
    FOREIGN KEY(joueur) REFERENCES joueur(id),
    PRIMARY KEY(id AUTOINCREMENT)
);"""

T_DONNE = """
CREATE TABLE donne (
    id INTEGER NOT NULL UNIQUE,
    session INTEGER NOT NULL,
    nb_bout INTEGER NOT NULL,
    contrat TEXT NOT NULL,
    tete TEXT,
    point REAL NOT NULL,
    petit TEXT,
    poignee TEXT,
    pt_chelem TEXT,
    gd_chelem TEXT,
    PRIMARY KEY(id AUTOINCREMENT),
    FOREIGN KEY(session) REFERENCES session(id)
);"""

T_PRENEUR = """
CREATE TABLE preneur (
    id INTEGER NOT NULL UNIQUE,
    donne INTEGER NOT NULL UNIQUE,
    joueur INTEGER NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT),
    FOREIGN KEY(joueur) REFERENCES joueur(id),
    FOREIGN KEY(donne) REFERENCES donne(id)
);"""

T_APPELE = """
CREATE TABLE appele (
    id INTEGER NOT NULL UNIQUE,
    donne INTEGER NOT NULL UNIQUE,
    joueur INTEGER NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT),
    FOREIGN KEY(donne) REFERENCES donne(id),
    FOREIGN KEY(joueur) REFERENCES joueur(id)
);"""

T_DEFENSE = """
CREATE TABLE defense (
    id INTEGER NOT NULL UNIQUE,
    donne INTEGER NOT NULL,
    joueur INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT),
    FOREIGN KEY(joueur) REFERENCES joueur(id),
    FOREIGN KEY(donne) REFERENCES donne(id)
);"""

T_PNJ = """
CREATE TABLE pnj (
    id INTEGER NOT NULL UNIQUE,
    donne INTEGER NOT NULL UNIQUE,
    joueur INTEGER NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT),
    FOREIGN KEY(joueur) REFERENCES joueur(id),
    FOREIGN KEY(donne) REFERENCES donne(id)
);"""

INIT_JOUEUR = """
INSERT INTO joueur (pseudo, actif, protege)
VALUES ("Chien", 0, 1), ("Solo", 0, 1);
"""
