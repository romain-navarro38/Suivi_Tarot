from sqlalchemy import select, update, and_

import database.models as md
from api.utils import DATA_FILE


def init_bdd():
    """Création de la base de données et insertion des joueurs
    non jouables Chien et Solo utilent aux parties à 5 et 6 joueurs"""
    md.Base.metadata.create_all(md.engine)

    insert_new_player({'nickname': 'Chien', 'active': False, 'protect': True})
    insert_new_player({'nickname': 'Solo', 'active': False, 'protect': True})

def insert_new_partie(**partie) -> int:
    """Insère les données d'une session ainsi que les donnes associées"""
    partie = md.Partie(**partie)
    md.session.add(partie)
    md.session.commit()
    return partie.id

def insert_players_partie(partie_id: int, players: list[str]):
    """Insère l'id des joueurs ayant participé à une partie dans la
    table de jointure partie_joueur"""
    for player in players:
        player_id = get_player_id(player)
        partie_player = md.PartiePlayer(partie_id=partie_id, player_id=player_id)
        md.session.add(partie_player)
    md.session.commit()

def insert_donne(donne: md.Donne) -> int:
    """Insère une donne dans la bdd et retourne son id
    généré automatiquement"""
    md.session.add(donne)
    md.session.commit()
    return donne.id

def insert_preneur(donne_id: int, nickname: str):
    """Enregistre en bdd l'id du joueur ayant participé à une donne
    comme preneur"""
    joueur_id = get_player_id(nickname)
    md.session.add(md.Preneur(donne_id=donne_id, player_id=joueur_id))
    md.session.commit()

def insert_appele(donne_id: int, nickname: str):
    """Enregistre en bdd l'id du joueur ayant participé à une donne
    comme appele (partie à 5 ou 6 joueurs uniquement)"""
    player_id = get_player_id(nickname)
    md.session.add(md.Appele(donne_id=donne_id, player_id=player_id))
    md.session.commit()

def insert_pnj(donne_id: int, nickname: str):
    """Enregistre en bdd l'id du joueur ayant participé à une donne
    comme pnj (partie à 6 joueurs uniquement)"""
    player_id = get_player_id(nickname)
    md.session.add(md.Pnj(donne_id=donne_id, player_id=player_id))
    md.session.commit()

def insert_defense(donne_id: int, nickname: str, number: int):
    """Enregistre en bdd l'id du joueur ayant participé à une donne
    comme defenseur"""
    player_id = get_player_id(nickname)
    md.session.add(md.Defense(donne_id=donne_id, player_id=player_id, numero=number))
    md.session.commit()

def get_player_id(nickname: str) -> int:
    """Retourne l'id d'un joueur en fonction de son pseudo"""
    statement = select(md.Player.id).where(md.Player.nickname == nickname)
    player_id = md.session.execute(statement).first()
    return player_id[0]

def insert_new_player(player: dict):
    """Insertion en bdd d'un joueur. Dictionnaire du type :
    {'pseudo': str, 'nom': str|None, 'prenom': str|None, 'actif': bool, 'protege': bool}"""
    md.session.add(md.Player(**player))
    md.session.commit()

def get_all_players() -> list[str]:
    """Retourne la liste de tous les joueurs"""
    players = md.session.execute(select(md.Player.nickname))
    return players.scalars().all()

def get_active_players() -> list[str]:
    """Retourne la liste des joueurs actifs"""
    statement = select(md.Player.nickname).where(md.Player.active == True)
    players = md.session.execute(statement)
    return players.scalars().all()

def get_inactive_players() -> list[str]:
    """Retourne la liste des joueurs inactifs"""
    statement = select(md.Player.nickname).where(
                        and_(
                            md.Player.active == False,
                            md.Player.protect == False
                        ))
    players = md.session.execute(statement)
    return players.scalars().all()

def update_status_joueurs(status_player: dict):
    """Met à jour le champ actif d'un ou plusieurs joueurs
    à partir d'un dictionnaire du type {"pseudo": bool}"""
    for nickname, status in status_player.items():
        statement = update(md.Player).where(md.Player.nickname == nickname).values(active=status).\
            execution_options(synchronize_session='fetch')
        md.session.execute(statement)
    md.session.commit()


if __name__ == '__main__':
    if not DATA_FILE.exists():
        init_bdd()
