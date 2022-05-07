"""Représentation sous forme de classes via SQLAlchemy de la bdd"""

from sqlalchemy import create_engine, Integer, Column, String, Boolean, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from suivi_tarot.api.calcul import Contract, Poignee
from suivi_tarot.api.utils import DATA_FILE


engine = create_engine(f'sqlite:///{DATA_FILE}', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Player(Base):
    """Représente un joueur, il peut être actif ou non. Contient aussi des instances non
    jouables (attribut protege) utilent aux parties à 5 ou 6 joueurs (Alone, Chien, Solo)."""
    __tablename__ = 'player'

    id_player = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String, unique=True, nullable=False)
    surname = Column(String)
    firstname = Column(String)
    active = Column(Boolean, nullable=False)
    protect = Column(Boolean, nullable=False)

    game_player = relationship('GamePlayer', back_populates='player')
    preneur = relationship('Preneur', back_populates='player')
    appele = relationship('Appele', back_populates='player')
    defense = relationship('Defense', back_populates='player')
    pnj = relationship('Pnj', back_populates='player')

    def __repr__(self):
        return f"Player(id: {self.id}, nickname: {self.pseudo}, nom: {self.nom}, prenom: {self.prenom}, " \
               f"actif: {self.actif}, protege: {self.protege})"


class Game(Base):
    """Représente une partie avec sa date et le nombre de joueurs présents."""
    __tablename__ = 'game'

    id_game = Column(Integer, primary_key=True, autoincrement=True)
    date_ = Column(DateTime, unique=True, nullable=False)
    table_ = Column(Integer, nullable=False)

    game_player = relationship('GamePlayer', back_populates='game')
    donne = relationship('Donne', back_populates='game')

    def __repr__(self):
        return f"Game(id: {self.id}, date: {self.date_}, table: {self.table_})"


class GamePlayer(Base):
    """Association d'une partie aux joueurs la disputant."""
    __tablename__ = 'game_player'

    id_game_player = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('game.id_game'), nullable=False)
    player_id = Column(Integer, ForeignKey('player.id_player'), nullable=False)

    game = relationship('Game', back_populates='game_player')
    player = relationship('Player', back_populates='game_player')


class Donne(Base):
    """Représente les donnes d'une partie."""
    __tablename__ = 'donne'

    id_donne = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('game.id_game'), nullable=False)
    nb_bout = Column(Integer, nullable=False)
    contract = Column(Enum(Contract), nullable=False)
    tete = Column(String)
    point = Column(Float, nullable=False)
    petit = Column(String)
    poignee = Column(Enum(Poignee))
    petit_chelem = Column(String)
    grand_chelem = Column(String)

    game = relationship('Game', back_populates='donne')
    preneur = relationship('Preneur', back_populates='donne')
    appele = relationship('Appele', back_populates='donne')
    defense = relationship('Defense', back_populates='donne')
    pnj = relationship('Pnj', back_populates='donne')


class Preneur(Base):
    """Représente le joueur ayant fait la plus grande enchère (contrat) d'une donne."""
    __tablename__ = 'preneur'

    id_preneur = Column(Integer, primary_key=True, autoincrement=True)
    donne_id = Column(Integer, ForeignKey('donne.id_donne'), unique=True, nullable=False)
    player_id = Column(Integer, ForeignKey('player.id_player'), nullable=False)

    donne = relationship('Donne', back_populates='preneur')
    player = relationship('Player', back_populates='preneur')


class Appele(Base):
    """Représente le joueur ayant été appelé par le preneur lors d'une donne.
    Seulement pour les parties à 5 ou 6 joueurs"""
    __tablename__ = 'appele'

    id_appele = Column(Integer, primary_key=True, autoincrement=True)
    donne_id = Column(Integer, ForeignKey('donne.id_donne'), unique=True, nullable=False)
    player_id = Column(Integer, ForeignKey('player.id_player'), nullable=False)

    donne = relationship('Donne', back_populates='appele')
    player = relationship('Player', back_populates='appele')


class Defense(Base):
    """Représente les joueurs qui ne sont ni preneur, appele ou pnj d'une donne."""
    __tablename__ = 'defense'

    id_defense = Column(Integer, primary_key=True, autoincrement=True)
    donne_id = Column(Integer, ForeignKey('donne.id_donne'), nullable=False)
    player_id = Column(Integer, ForeignKey('player.id_player'), nullable=False)
    number = Column(Integer, nullable=False)

    donne = relationship('Donne', back_populates='defense')
    player = relationship('Player', back_populates='defense')


class Pnj(Base):
    """Représente pour une donne le joueur ne l'ayant pas disputé.
    Seulement pour les parties à 6 joueurs"""
    __tablename__ = 'pnj'

    id_pnj = Column(Integer, primary_key=True, autoincrement=True)
    donne_id = Column(Integer, ForeignKey('donne.id_donne'), unique=True, nullable=False)
    player_id = Column(Integer, ForeignKey('player.id_player'), nullable=False)

    donne = relationship('Donne', back_populates='pnj')
    player = relationship('Player', back_populates='pnj')
