from math import ceil, floor
from enum import Enum


class CoefContrat(Enum):
    """Enumération des contrats possibles associés à leur coefficient"""
    G = 2   # Garde
    GS = 4  # Garde Sans
    GC = 6  # Garde Contre

class Poignee(Enum):
    """Enumération des annonces de poignée possibles associés à leur valeur"""
    Simple = 20  # nombre d'atouts : 18 à 3 joueurs, 15 à 4 joueurs ou 13 à 5 joueurs
    Double = 30  # 15, 13 ou 10
    Triple = 40  # 13, 10 ou 8


def calcul_donne(contrat: str, bout: str, point: float, poignee: str,
                 petit_au_bout: str, petit_chelem: str, grand_chelem: str):
    """Retourne le résultat d'une donne."""
    coef = valeur_coefficient(contrat)
    cible = valeur_cible(bout)
    point, signe = valeurs_donne(point, cible)
    resultat = base_resultat(cible, point, coef)

    if poignee:
        resultat += ajout_poignee(poignee)
    if petit_au_bout:
        resultat += ajout_petit_au_bout(petit_au_bout, coef, signe)
    if petit_chelem:
        resultat += ajout_petit_chelem(signe)
    if grand_chelem:
        resultat += ajout_grand_chelem(grand_chelem, signe)

    return resultat * signe

def valeur_coefficient(contrat: str) -> int:
    """Retourne la valeur du coefficient multiplicateur qui est fonction du contrat
    choisi par le preneur avant de commencer une donne."""
    for coef_contrat in CoefContrat:
        if contrat == coef_contrat.name:
            return coef_contrat.value

def valeur_cible(bout: str) -> int:
    """Retourne le nombre de point que le preneur doit atteindre pour gagner
    une donne. Cette cible est fonction du nombre de bouts qu'il a en fin de donne."""
    valeur = {
        "0": 56,
        "1": 51,
        "2": 41,
        "3": 36
    }
    return valeur[bout]

def valeurs_donne(point: float, cible: int) -> tuple[int, int]:
    """Retourne le score du preneur arrondi à l'entier supérieur ou inférieur
    en fonction de s'il a respectivement gagné ou perdu la donne."""
    if point < cible:
        signe = -1
        point = floor(point)
    else:
        signe = 1
        point = ceil(point)
    return point, signe

def base_resultat(cible: int, point: int, coef: int) -> int:
    """Retourne la valeur brute de la donne."""
    return (abs(cible - point) + 25) * coef

def ajout_poignee(annonce: str) -> int:
    """Retourne le bonus correspondant à une poignée."""
    for poignee in Poignee:
        if annonce == poignee.name:
            return poignee.value

def ajout_petit_au_bout(annonce: str, coef: int, signe: int) -> int:
    """Retourne le bonus/malus d'un petit au bout"""
    return 10 * coef * signe if annonce == "Gagné" else -10 * coef * signe

def ajout_petit_chelem(signe: int) -> int:
    """Retourne le bonus/malus pour la réalisation d'un petit chelem (tous les plis sauf un)."""
    return 200 * signe

def ajout_grand_chelem(annonce: str, signe: int) -> int:
    """Retourne le bonus/malus pour la réalisation d'un grand chelem (tous les plis)."""
    valeur = {
        "Réussi": -200,
        "Réussi ss annonce": 200,
        "Raté": 400
    }
    return valeur[annonce] * signe

def point_preneur_float(point: str, preneur: bool) -> float:
    return float(point) if preneur else 91 - float(point)
