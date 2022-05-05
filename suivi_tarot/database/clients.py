import datetime

import pandas as pd
from sqlalchemy import select, update, and_, func, between

import suivi_tarot.database.models as md
from suivi_tarot.api.utils import DATA_FILE


def init_bdd():
    """Création de la base de données et insertion des joueurs
    non jouables Chien et Solo utilent aux parties à 5 et 6 joueurs"""
    md.Base.metadata.create_all(md.engine)

    insert_new_player({'nickname': 'Chien', 'active': False, 'protect': True})
    insert_new_player({'nickname': 'Solo', 'active': False, 'protect': True})


def insert_new_partie(**partie) -> int:
    """Insère les données d'une partie ainsi que les donnes associées"""
    partie = md.Partie(**partie)
    md.session.add(partie)
    md.session.commit()
    return partie.id_partie


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
    return donne.id_donne


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
    md.session.add(md.Defense(donne_id=donne_id, player_id=player_id, number=number))
    md.session.commit()


def get_player_id(nickname: str) -> int:
    """Retourne l'id d'un joueur en fonction de son pseudo"""
    statement = select(md.Player.id_player).where(md.Player.nickname == nickname)
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
        statement = update(md.Player).where(md.Player.nickname == nickname).values(active=status). \
            execution_options(synchronize_session='fetch')
        md.session.execute(statement)
    md.session.commit()


def get_distinct_years() -> list[str]:
    """Retourne la liste des années en ordre decroissant où au moins une
    partie a été jouée"""
    from sqlalchemy import extract, desc

    years = md.session.query(extract('year', md.Partie.date_).label('year')) \
        .distinct().order_by(desc('year'))
    return [str(year[0]) for year in years]


def get_min_max_dates_parties() -> tuple[datetime.datetime | None, datetime.datetime | None]:
    """Retourne les dates, datetime, de la première et de la dernière partie enregistée.
    Si la bdd est vide, retourne un tuple de None."""
    query = md.session.query(func.min(md.Partie.date_), func.max(md.Partie.date_)).all()
    return query[0][0], query[0][1]


def get_donne(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> pd.DataFrame:
    """Retourne un DataFrame de toutes les parties et donnes jouées dans une période donnée
    et pour un nombre de joueurs"""
    query = select(md.Partie.id_partie,
                   md.Partie.date_,
                   md.Partie.table_,
                   md.Donne.id_donne,
                   md.Donne.contract,
                   md.Donne.nb_bout,
                   md.Donne.tete,
                   md.Donne.point,
                   md.Donne.petit,
                   md.Donne.poignee,
                   md.Donne.petit_chelem,
                   md.Donne.grand_chelem) \
        .join(md.Partie).where(and_(between(md.Partie.date_, start_date, end_date),
                                    md.Partie.table_ == nombre_joueurs))
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_preneur(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> pd.DataFrame:
    """Retourne un DataFrame de tous les joueurs ayant le rôle de preneur parmis les donnes jouées
    dans une période donnée avec un certain nombre de joueurs"""
    query = select(md.Donne.id_donne, md.Player.nickname).select_from(md.Player) \
        .join(md.Preneur, md.Player.id_player == md.Preneur.player_id) \
        .join(md.Donne, md.Preneur.donne_id == md.Donne.id_donne) \
        .join(md.Partie, md.Donne.partie_id == md.Partie.id_partie) \
        .where(and_(between(md.Partie.date_, start_date, end_date)),
               md.Partie.table_ == nombre_joueurs)
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_appele(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> pd.DataFrame:
    """Retourne un DataFrame de tous les joueurs ayant le rôle d'appelé parmis les donnes jouées
    dans une période donnée avec un certain nombre de joueurs"""
    query = select(md.Donne.id_donne, md.Player.nickname).select_from(md.Player) \
        .join(md.Appele, md.Player.id_player == md.Appele.player_id) \
        .join(md.Donne, md.Appele.donne_id == md.Donne.id_donne) \
        .join(md.Partie, md.Donne.partie_id == md.Partie.id_partie) \
        .where(and_(between(md.Partie.date_, start_date, end_date)),
               md.Partie.table_ == nombre_joueurs)
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_defense(start_date: datetime, end_date: datetime, nombre_joueurs: int, num: int) -> pd.DataFrame:
    """Retourne un DataFrame de tous les joueurs ayant le rôle de défenseur parmis les donnes jouées
    dans une période donnée avec un certain nombre de joueurs"""
    query = select(md.Donne.id_donne, md.Player.nickname).select_from(md.Player) \
        .join(md.Defense, md.Player.id_player == md.Defense.player_id) \
        .join(md.Donne, md.Defense.donne_id == md.Donne.id_donne) \
        .join(md.Partie, md.Donne.partie_id == md.Partie.id_partie) \
        .where(and_(between(md.Partie.date_, start_date, end_date)),
               md.Partie.table_ == nombre_joueurs,
               md.Defense.number == num)
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_pnj(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> pd.DataFrame:
    """Retourne un DataFrame de tous les joueurs ayant le rôle de pnj parmis les donnes jouées
    dans une période donnée avec un certain nombre de joueurs"""
    query = select(md.Donne.id_donne, md.Player.nickname).select_from(md.Player) \
        .join(md.Pnj, md.Player.id_player == md.Pnj.player_id) \
        .join(md.Donne, md.Pnj.donne_id == md.Donne.id_donne) \
        .join(md.Partie, md.Donne.partie_id == md.Partie.id_partie) \
        .where(and_(between(md.Partie.date_, start_date, end_date)),
               md.Partie.table_ == nombre_joueurs)
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_distinct_player(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> list[str]:
    """Retourne la liste de tous les joueurs ayant joué au moins une donne"""
    query = select(md.Player.nickname).distinct().select_from(md.Player) \
        .join(md.PartiePlayer, md.Player.id_player == md.PartiePlayer.player_id) \
        .join(md.Partie, md.PartiePlayer.partie_id == md.Partie.id_partie) \
        .where(and_(between(md.Partie.date_, start_date, end_date)),
               md.Partie.table_ == nombre_joueurs)
    return md.engine.execute(query).scalars().all()


if __name__ == '__main__':
    if not DATA_FILE.exists():
        init_bdd()
    nb = 3
    depart = datetime.datetime(2022, 1, 1)
    fin = datetime.datetime(2022, 12, 31)
    print(get_distinct_player(depart, fin, nb))

