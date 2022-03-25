from sqlalchemy import select, update, and_

import database.models as md
from api.utils import DATA_FILE


def init_bdd():
    """Création de la base de données et insertion des joueurs
    non jouables Chien et Solo utilent aux parties à 5 et 6 joueurs"""
    md.Base.metadata.create_all(md.engine)

    insert_new_joueur({'pseudo': 'Chien', 'actif': False, 'protege': True})
    insert_new_joueur({'pseudo': 'Solo', 'actif': False, 'protege': True})

def insert_new_partie(**partie) -> int:
    """Insère les données d'une session ainsi que les donnes associées"""
    partie = md.Partie(**partie)
    md.session.add(partie)
    md.session.commit()
    return partie.id

def insert_joueurs_partie(partie_id: int, joueurs: list[str]):
    """Insère l'id des joueurs ayant participé à une partie dans la
    table de jointure partie_joueur"""
    for joueur in joueurs:
        joueur_id = get_id_joueur(joueur)
        partie_joueur = md.PartieJoueur(partie_id=partie_id, joueur_id=joueur_id)
        md.session.add(partie_joueur)
    md.session.commit()

def insert_donne(donne: md.Donne) -> int:
    """Insère une donne dans la bdd et retourne son id
    généré automatiquement"""
    md.session.add(donne)
    md.session.commit()
    return donne.id

def insert_preneur(donne_id: int, pseudo: str):
    """Enregistre en bdd l'id du joueur ayant participé à une donne
    comme preneur"""
    joueur_id = get_id_joueur(pseudo)
    md.session.add(md.Preneur(donne_id=donne_id, joueur_id=joueur_id))
    md.session.commit()

def insert_appele(donne_id: int, pseudo: str):
    """Enregistre en bdd l'id du joueur ayant participé à une donne
    comme appele (partie à 5 ou 6 joueurs uniquement)"""
    joueur_id = get_id_joueur(pseudo)
    md.session.add(md.Appele(donne_id=donne_id, joueur_id=joueur_id))
    md.session.commit()

def insert_pnj(donne_id: int, pseudo: str):
    """Enregistre en bdd l'id du joueur ayant participé à une donne
    comme pnj (partie à 6 joueurs uniquement)"""
    joueur_id = get_id_joueur(pseudo)
    md.session.add(md.Pnj(donne_id=donne_id, joueur_id=joueur_id))
    md.session.commit()

def insert_defense(donne_id: int, pseudo: str, numero: int):
    """Enregistre en bdd l'id du joueur ayant participé à une donne
    comme defenseur"""
    joueur_id = get_id_joueur(pseudo)
    md.session.add(md.Defense(donne_id=donne_id, joueur_id=joueur_id, numero=numero))
    md.session.commit()

def get_id_joueur(pseudo: str) -> int:
    """Retourne l'id d'un joueur en fonction de son pseudo"""
    stmt = select(md.Joueur.id).where(md.Joueur.pseudo == pseudo)
    id_joueur = md.session.execute(stmt).first()
    return id_joueur[0]

def insert_new_joueur(joueur: dict):
    """Insertion en bdd d'un joueur. Dictionnaire du type :
    {'pseudo': str, 'nom': str|None, 'prenom': str|None, 'actif': bool, 'protege': bool}"""
    md.session.add(md.Joueur(**joueur))
    md.session.commit()

def get_joueur_actif() -> list[str]:
    """Retourne la liste de tous les joueurs"""
    stmt = select(md.Joueur.pseudo).where(md.Joueur.actif == True)
    joueurs = md.session.execute(stmt)
    return joueurs.scalars().all()

def get_all_joueur() -> list[str]:
    """Retourne la liste des joueurs actifs"""
    joueurs = md.session.execute(select(md.Joueur.pseudo))
    return joueurs.scalars().all()

def get_joueur_inactif() -> list[str]:
    """Retourne la liste des joueurs inactifs"""
    stmt = select(md.Joueur.pseudo).where(
                        and_(
                            md.Joueur.actif == False,
                            md.Joueur.protege == False
                        ))
    joueurs = md.session.execute(stmt)
    return joueurs.scalars().all()

def update_status_joueurs(joueur_status: dict):
    """Met à jour le champ actif d'un ou plusieurs joueurs
    à partir d'un dictionnaire du type {"pseudo": bool}"""
    for pseudo, status in joueur_status.items():
        stmt = update(md.Joueur).where(md.Joueur.pseudo == pseudo).values(actif=status).\
            execution_options(synchronize_session='fetch')
        md.session.execute(stmt)
    md.session.commit()


if __name__ == '__main__':
    if not DATA_FILE.exists():
        init_bdd()
