"""Représentation sous forme de classes via SQLAlchemy de la bdd"""

from sqlalchemy import create_engine, Integer, Column, String, Boolean, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from api.calcul import Contrat, Poignee
from api.utils import DATA_FILE


engine = create_engine(f'sqlite:///{DATA_FILE}', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Joueur(Base):
    """Représente un joueur, il peut être actif ou non. Contient aussi des instances non
    jouables (attribut protege) utilent aux parties à 5 ou 6 joueurs (Alone, Chien, Solo)."""
    __tablename__ = 'joueur'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pseudo = Column(String, unique=True, nullable=False)
    nom = Column(String)
    prenom = Column(String)
    actif = Column(Boolean, nullable=False)
    protege = Column(Boolean, nullable=False)

    partie_joueur = relationship('PartieJoueur', back_populates='joueur')
    preneur = relationship('Preneur', back_populates='joueur')
    appele = relationship('Appele', back_populates='joueur')
    defense = relationship('Defense', back_populates='joueur')
    pnj = relationship('Pnj', back_populates='joueur')

    def __repr__(self):
        return f"Joueur(id: {self.id}, pseudo: {self.pseudo}, nom: {self.nom}, prenom: {self.prenom}," \
               f" actif: {self.actif}, protege: {self.protege})"

class Partie(Base):
    """Représente une partie avec sa date et le nombre de joueurs présents."""
    __tablename__ = 'partie'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_ = Column(DateTime, unique=True, nullable=False)
    table_ = Column(Integer, nullable=False)

    partie_joueur = relationship('PartieJoueur', back_populates='partie')
    donne = relationship('Donne', back_populates='partie')

    def __repr__(self):
        return f"Partie(id: {self.id}, date: {self.date_}, table: {self.table_})"

class PartieJoueur(Base):
    """Association d'une partie aux joueurs la disputant."""
    __tablename__ = 'partie_joueur'

    id = Column(Integer, primary_key=True, autoincrement=True)
    partie_id = Column(Integer, ForeignKey('partie.id'), nullable=False)
    joueur_id = Column(Integer, ForeignKey('joueur.id'), nullable=False)

    partie = relationship('Partie', back_populates='partie_joueur')
    joueur = relationship('Joueur', back_populates='partie_joueur')

class Donne(Base):
    """Représente les donnes d'une partie."""
    __tablename__ = 'donne'

    id = Column(Integer, primary_key=True, autoincrement=True)
    partie_id = Column(Integer, ForeignKey('partie.id'), nullable=False)
    nb_bout = Column(Integer, nullable=False)
    contrat = Column(Enum(Contrat), nullable=False)
    tete = Column(String)
    point = Column(Float, nullable=False)
    petit = Column(String)
    poignee = Column(Enum(Poignee))
    pt_chelem = Column(String)
    gd_chelem = Column(String)

    partie = relationship('Partie', back_populates='donne')
    preneur = relationship('Preneur', back_populates='donne')
    appele = relationship('Appele', back_populates='donne')
    defense = relationship('Defense', back_populates='donne')
    pnj = relationship('Pnj', back_populates='donne')


class Preneur(Base):
    """Représente le joueur ayant fait la plus grande enchère (contrat) d'une donne."""
    __tablename__ = 'preneur'

    id = Column(Integer, primary_key=True, autoincrement=True)
    donne_id = Column(Integer, ForeignKey('donne.id'), unique=True, nullable=False)
    joueur_id = Column(Integer, ForeignKey('joueur.id'), nullable=False)

    donne = relationship('Donne', back_populates='preneur')
    joueur = relationship('Joueur', back_populates='preneur')

class Appele(Base):
    """Représente le joueur ayant été appelé par le preneur lors d'une donne.
    Seulement pour les parties à 5 ou 6 joueurs"""
    __tablename__ = 'appele'

    id = Column(Integer, primary_key=True, autoincrement=True)
    donne_id = Column(Integer, ForeignKey('donne.id'), unique=True, nullable=False)
    joueur_id = Column(Integer, ForeignKey('joueur.id'), nullable=False)

    donne = relationship('Donne', back_populates='appele')
    joueur = relationship('Joueur', back_populates='appele')

class Defense(Base):
    """Représente les joueurs qui ne sont ni preneur, appele ou pnj d'une donne."""
    __tablename__ = 'defense'

    id = Column(Integer, primary_key=True, autoincrement=True)
    donne_id = Column(Integer, ForeignKey('donne.id'), nullable=False)
    joueur_id = Column(Integer, ForeignKey('joueur.id'), nullable=False)
    numero = Column(Integer, nullable=False)

    donne = relationship('Donne', back_populates='defense')
    joueur = relationship('Joueur', back_populates='defense')

class Pnj(Base):
    """Représente pour une donne le joueur ne l'ayant pas disputé.
    Seulement pour les parties à 6 joueurs"""
    __tablename__ = 'pnj'

    id = Column(Integer, primary_key=True, autoincrement=True)
    donne_id = Column(Integer, ForeignKey('donne.id'), unique=True, nullable=False)
    joueur_id = Column(Integer, ForeignKey('joueur.id'), nullable=False)

    donne = relationship('Donne', back_populates='pnj')
    joueur = relationship('Joueur', back_populates='pnj')
