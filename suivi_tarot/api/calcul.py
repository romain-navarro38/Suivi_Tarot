from math import ceil, floor
from enum import Enum


class Contract(Enum):
    """Enumération des contrats possibles associés à leur coefficient"""
    G = 2  # Garde
    GS = 4  # Garde Sans
    GC = 6  # Garde Contre


class Poignee(Enum):
    """Enumération des annonces de poignée possibles associés à leur valeur"""
    No = 0  # pas d'annonce
    Simple = 20  # nombre d'atouts : 18 à 3 joueurs, 15 à 4 joueurs ou 13 à 5 joueurs
    Double = 30  # 15, 13 ou 10
    Triple = 40  # 13, 10 ou 8


def conversion_contract(choix_contrat: str) -> Contract:
    """Retourne l'élément de la classe Contrat correspondant à la valeur textuelle"""
    for contrat in Contract:
        if choix_contrat == contrat.name:
            return contrat


def conversion_poignee(choix_poignee: str) -> Poignee | None:
    """Retourne l'élément de la classe Poignee correspondant à la valeur textuelle"""
    return next((poignee for poignee in Poignee if choix_poignee == poignee.name), Poignee.No)


def calcul_donne(contract: Contract, bout: str, point: float, poignee: Poignee | str,
                 petit_au_bout: str, petit_chelem: str, grand_chelem: str):
    """Retourne le résultat d'une donne."""
    coef = contract_coef_value(contract)
    target = target_value(bout)
    point, sign = donne_values(point, target)
    result = base_result(target, point, coef)

    if poignee:
        result += add_poignee(poignee)
    if petit_au_bout:
        result += add_petit_au_bout(petit_au_bout, coef, sign)
    if petit_chelem:
        result += add_petit_chelem(sign)
    if grand_chelem:
        result += add_grand_chelem(grand_chelem, sign)

    return result * sign


def contract_coef_value(contract: Contract) -> int:
    """Retourne la valeur du coefficient associé au contrat
    choisi par le preneur avant de commencer une donne."""
    for coef_contract in Contract:
        if contract == coef_contract:
            return coef_contract.value


def target_value(bout: str) -> int:
    """Retourne le nombre de point que le preneur doit atteindre pour gagner
    une donne. Cette cible est fonction du nombre de bouts qu'il a en fin de donne."""
    value = {
        "0": 56,
        "1": 51,
        "2": 41,
        "3": 36
    }
    return value[bout]


def donne_values(point: float, target: int) -> tuple[int, int]:
    """Retourne le score du preneur arrondi à l'entier supérieur ou inférieur
    en fonction de s'il a respectivement gagné ou perdu la donne."""
    if point < target:
        signe = -1
        point = floor(point)
    else:
        signe = 1
        point = ceil(point)
    return point, signe


def base_result(target: int, point: int, coef: int) -> int:
    """Retourne la valeur brute de la donne."""
    return (abs(target - point) + 25) * coef


def add_poignee(annonce: Poignee) -> int:
    """Retourne le bonus correspondant à une poignée."""
    for poignee in Poignee:
        if annonce == poignee:
            return poignee.value


def add_petit_au_bout(annonce: str, coef: int, sign: int) -> int:
    """Retourne le bonus/malus d'un petit joué au dernier pli de la donne"""
    return 10 * coef * sign if annonce == "Gagné" else -10 * coef * sign


def add_petit_chelem(sign: int) -> int:
    """Retourne le bonus/malus pour la réalisation d'un petit chelem (tous les plis sauf un)."""
    return 200 * sign


def add_grand_chelem(annonce: str, sign: int) -> int:
    """Retourne le bonus/malus pour la réalisation d'un grand chelem (tous les plis)."""
    value = {
        "Réussi": 400,
        "Réussi ss annonce": 200,
        "Raté": -200
    }
    return value[annonce] * sign


def point_preneur_float(point: str, is_attack: bool) -> float:
    """Retourne les points de l'attaque convertis en float"""
    return float(point) if is_attack else 91 - float(point)


def distribution_point_between_attack_defense(result: int,
                                              appele: str,
                                              number_players: int
                                              ) -> tuple[int, int | str, int]:
    """Retourne les points les points à attribuer entre l'attaque et la défense
    en fonction du résultat d'une donne"""
    if appele in {"Chien", "Solo"}:
        coef = 4
        appele = ''
    elif number_players == 3 or number_players > 4:
        coef = 2
        appele = result
    else:
        coef = 3
        appele = ''
    preneur = result * coef
    defense = result * -1
    return preneur, appele, defense


def repartition_points_by_player(donne: dict, player: str, table_of: int) -> int:
    """Retourne les points à attribuer un à joueur en fonction de son rôle
    dans une donne"""
    nickname = player

    match table_of:
        case 5:
            if nickname in [donne['pnj'], donne['preneur'], donne['appele']]:
                if nickname == donne['pnj']:
                    return 0
                elif nickname == donne['appele']:
                    return donne['result']
                else:
                    return donne['result'] * 4 if donne['appele'] in ['Chien', 'Solo'] else donne['result'] * 2
            elif nickname in [donne['defense1'], donne['defense2'], donne['defense3'], donne['defense4']]:
                return donne['result'] * -1
            else:
                return 0
        case 4:
            return donne['result'] * 3 if nickname == donne['preneur'] else donne['result'] * -1
        case 3:
            return donne['result'] * 2 if nickname == donne['preneur'] else donne['result'] * -1
