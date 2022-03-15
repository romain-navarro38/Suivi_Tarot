import sqlite3

from api.utils import DATA_FILE, T_JOUEUR, T_SESSION, T_SESSION_JOUEUR, \
    T_DONNE, T_PRENEUR, T_APPELE, T_DEFENSE, T_PNJ, INIT_JOUEUR


def verif_bdd_exist():
    return DATA_FILE.exists()

def init_bdd():
    """Crée une bdd vierge"""
    db = sqlite3.connect(DATA_FILE)
    c = db.cursor()
    c.execute(T_JOUEUR)
    c.execute(T_SESSION)
    c.execute(T_SESSION_JOUEUR)
    c.execute(T_DONNE)
    c.execute(T_PRENEUR)
    c.execute(T_APPELE)
    c.execute(T_DEFENSE)
    c.execute(T_PNJ)
    c.execute(INIT_JOUEUR)
    db.commit()
    db.close()

def ajout_session(**session):
    """Insère les données d'une session ainsi que les donnes associées"""
    db = sqlite3.connect(DATA_FILE)
    c = db.cursor()

    c.execute("INSERT INTO session (date_, table_) VALUES (:date_, :table_)", session)
    id_session = get_last_id(c)

    for joueur in session["joueurs"]:
        c.execute(f"INSERT INTO session_joueur (session, joueur) VALUES ({id_session}, {get_id_joueur(c, joueur)})")

    for donne in range(session["nb_donne"]):
        c.execute(f"""
        INSERT INTO donne (session, nb_bout, contrat, tete, point, petit, poignee, pt_chelem, gd_chelem) 
        VALUES ({id_session}, :nb_bout, :contrat, :tete, :point, :petit, :poignee, :pt_chelem, :gd_chelem)
        """, session[f"d{donne}"])
        id_donne = get_last_id(c)

        insert_donne_joueur(c, id_donne, "preneur", session[f"d{donne}"]["preneur"])

        if session["table_"] == 5:
            insert_donne_joueur(c, id_donne, "appele", session[f"d{donne}"]["appele"])

        if session.get(f"d{donne}").get("pnj", ""):
            insert_donne_joueur(c, id_donne, "pnj", session[f"d{donne}"]["pnj"])

        for i, joueur in enumerate(session[f"d{donne}"]["defense"], 1):
            insert_donne_joueur_defense(c, id_donne, joueur, i)

    db.commit()
    db.close()

def get_last_id(cursor):
    """Retourne le dernier id créé dans la bdd"""
    return cursor.execute("SELECT last_insert_rowid()").fetchone()[0]

def get_id_joueur(cursor, pseudo):
    """Retourne l'id d'un joueur à partir de son pseudo et du cursor d'une connexion sqlite3"""
    return cursor.execute(f"SELECT id FROM joueur WHERE pseudo='{pseudo}'").fetchone()[0]

def insert_donne_joueur(cursor, id_donne, table, pseudo):
    """Insère les données dans une des tables de jointures donne-joueur"""
    id_joueur = get_id_joueur(cursor, pseudo)
    cursor.execute(f"INSERT INTO {table} (donne, joueur) VALUES ({id_donne}, {id_joueur})")

def insert_donne_joueur_defense(cursor, id_donne, pseudo, numero):
    """Insère les données dans la table de jointure defense"""
    id_joueur = get_id_joueur(cursor, pseudo)
    cursor.execute(f"INSERT INTO defense (donne, joueur, numero) VALUES ({id_donne}, {id_joueur}, {numero})")

def get_joueur_actif():
    """Retourne la liste des joueurs actifs"""
    db = sqlite3.connect(DATA_FILE)
    c = db.cursor()
    c.execute("SELECT pseudo FROM joueur WHERE actif=1 AND protege=0")
    joueur = c.fetchall()
    db.close()
    return joueur

def get_joueur_inactif():
    """Retourne la liste des joueurs inactifs"""
    db = sqlite3.connect(DATA_FILE)
    c = db.cursor()
    c.execute("SELECT pseudo FROM joueur WHERE actif=0 AND protege=0")
    joueur = c.fetchall()
    db.close()
    return joueur

def get_joueur():
    """Retourne la liste de tous les joueurs"""
    db = sqlite3.connect(DATA_FILE)
    c = db.cursor()
    c.execute("SELECT pseudo FROM joueur")
    joueurs = c.fetchall()
    db.close()
    return joueurs

def maj_status_joueurs(joueur_status: dict):
    """Met à jour le champ actif d'un ou plusieurs joueurs
    à partir d'un dictionnaire du type {"pseudo": 0 ou 1}"""
    db = sqlite3.connect(DATA_FILE)
    c = db.cursor()
    for pseudo, status in joueur_status.items():
        c.execute(f'UPDATE joueur SET actif={status} WHERE pseudo="{pseudo}"')
    db.commit()
    db.close()

def ajout_joueur(joueur: dict):
    """Ajoute un joueur à la bdd à partir d'un dictionnaire du type
    {"pseudo": str, "nom": str, "prenom": str, "actif": 0 ou 1}.
    Le champ protege sera à 0"""
    db = sqlite3.connect(DATA_FILE)
    c = db.cursor()
    c.execute("""
    INSERT INTO joueur (pseudo, nom, prenom, actif, protege) 
    VALUES (:pseudo, :nom, :prenom, :actif, 0)
    """, joueur)
    db.commit()
    db.close()


# Si aucune bdd trouvée à initialisation de l'app, une vierge est créée
if not verif_bdd_exist():
    init_bdd()

if __name__ == '__main__':
    pass
