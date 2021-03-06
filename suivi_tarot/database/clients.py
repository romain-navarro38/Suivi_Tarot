import datetime

import pandas as pd
from sqlalchemy import select, update, and_, func, between

import suivi_tarot.database.models as md
from suivi_tarot.api.utils import hashage_password, move_database


def init_bdd(path: str, password: str):
    """Création de la base de données, insertion des joueurs
    non jouables Chien et Solo utilent aux parties à 5 et 6 joueurs
    ainsi que le hash du mot de passe et son sel"""
    md.Base.metadata.create_all(md.engine)

    insert_new_player({'nickname': 'Chien', 'active': False, 'protect': True})
    insert_new_player({'nickname': 'Solo', 'active': False, 'protect': True})

    hash_, salt = hashage_password(password)
    insert_hash_password({"hash_": hash_, "salt": salt})

    md.session.close()
    move_database(path)


def insert_hash_password(password):
    """Insère le hash du mot de passe et le sel associé"""
    md.session.add(md.Password(**password))
    md.session.commit()


def insert_new_game(**game) -> int:
    """Insère les données d'une partie ainsi que les donnes associées"""
    game = md.Game(**game)
    md.session.add(game)
    md.session.commit()
    return game.id_game


def insert_players_game(game_id: int, players: list[str]):
    """Insère l'id des joueurs ayant participé à une partie dans la
    table de jointure partie_joueur"""
    for player in players:
        player_id = get_player_id(player)
        game_player = md.GamePlayer(game_id=game_id, player_id=player_id)
        md.session.add(game_player)
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

    years = md.session.query(extract('year', md.Game.date_).label('year')) \
        .distinct().order_by(desc('year'))
    return [str(year[0]) for year in years]


def get_min_max_dates_games() -> tuple[datetime.datetime | None, datetime.datetime | None]:
    """Retourne les dates, datetime, de la première et de la dernière partie enregistée.
    Si la bdd est vide, retourne un tuple de None."""
    query = md.session.query(func.min(md.Game.date_), func.max(md.Game.date_)).all()
    return query[0][0], query[0][1]


def get_donne(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> pd.DataFrame:
    """Retourne un DataFrame de toutes les parties et donnes jouées dans une période donnée
    et pour un nombre de joueurs"""
    query = select(md.Game.id_game,
                   md.Game.date_,
                   md.Game.table_,
                   md.Donne.id_donne,
                   md.Donne.contract,
                   md.Donne.nb_bout,
                   md.Donne.tete,
                   md.Donne.point,
                   md.Donne.petit,
                   md.Donne.poignee,
                   md.Donne.petit_chelem,
                   md.Donne.grand_chelem) \
        .join(md.Game).where(and_(between(md.Game.date_, start_date, end_date),
                                  md.Game.table_ == nombre_joueurs))
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_preneur(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> pd.DataFrame:
    """Retourne un DataFrame de tous les joueurs ayant le rôle de preneur parmis les donnes jouées
    dans une période donnée avec un certain nombre de joueurs"""
    query = select(md.Donne.id_donne, md.Player.nickname).select_from(md.Player) \
        .join(md.Preneur, md.Player.id_player == md.Preneur.player_id) \
        .join(md.Donne, md.Preneur.donne_id == md.Donne.id_donne) \
        .join(md.Game, md.Donne.game_id == md.Game.id_game) \
        .where(and_(between(md.Game.date_, start_date, end_date)),
               md.Game.table_ == nombre_joueurs)
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_appele(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> pd.DataFrame:
    """Retourne un DataFrame de tous les joueurs ayant le rôle d'appelé parmis les donnes jouées
    dans une période donnée avec un certain nombre de joueurs"""
    query = select(md.Donne.id_donne, md.Player.nickname).select_from(md.Player) \
        .join(md.Appele, md.Player.id_player == md.Appele.player_id) \
        .join(md.Donne, md.Appele.donne_id == md.Donne.id_donne) \
        .join(md.Game, md.Donne.game_id == md.Game.id_game) \
        .where(and_(between(md.Game.date_, start_date, end_date)),
               md.Game.table_ == nombre_joueurs)
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_defense(start_date: datetime, end_date: datetime, nombre_joueurs: int, num: int) -> pd.DataFrame:
    """Retourne un DataFrame de tous les joueurs ayant le rôle de défenseur parmis les donnes jouées
    dans une période donnée avec un certain nombre de joueurs"""
    query = select(md.Donne.id_donne, md.Player.nickname).select_from(md.Player) \
        .join(md.Defense, md.Player.id_player == md.Defense.player_id) \
        .join(md.Donne, md.Defense.donne_id == md.Donne.id_donne) \
        .join(md.Game, md.Donne.game_id == md.Game.id_game) \
        .where(and_(between(md.Game.date_, start_date, end_date)),
               md.Game.table_ == nombre_joueurs,
               md.Defense.number == num)
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_pnj(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> pd.DataFrame:
    """Retourne un DataFrame de tous les joueurs ayant le rôle de pnj parmis les donnes jouées
    dans une période donnée avec un certain nombre de joueurs"""
    query = select(md.Donne.id_donne, md.Player.nickname).select_from(md.Player) \
        .join(md.Pnj, md.Player.id_player == md.Pnj.player_id) \
        .join(md.Donne, md.Pnj.donne_id == md.Donne.id_donne) \
        .join(md.Game, md.Donne.game_id == md.Game.id_game) \
        .where(and_(between(md.Game.date_, start_date, end_date)),
               md.Game.table_ == nombre_joueurs)
    return pd.read_sql_query(sql=query, con=md.engine, index_col="id_donne")


def get_distinct_player(start_date: datetime, end_date: datetime, nombre_joueurs: int) -> list[str]:
    """Retourne la liste de tous les joueurs ayant joué au moins une donne"""
    query = select(md.Player.nickname).distinct().select_from(md.Player) \
        .join(md.GamePlayer, md.Player.id_player == md.GamePlayer.player_id) \
        .join(md.Game, md.GamePlayer.game_id == md.Game.id_game) \
        .where(and_(between(md.Game.date_, start_date, end_date)),
               md.Game.table_ == nombre_joueurs)
    return md.engine.execute(query).scalars().all()


def get_hash_and_salt() -> tuple[str, str]:
    """Retourne le hash et sel stocké"""
    query = md.session.query(md.Password.hash_, md.Password.salt).where(md.Password.id_password == 1).all()
    return query[0][0], query[0][1]


if __name__ == '__main__':
    pwd, salt = get_hash_and_salt()
    print(pwd, salt)
