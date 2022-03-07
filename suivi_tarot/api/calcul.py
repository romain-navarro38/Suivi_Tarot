from math import ceil, floor


def calcul_donne(contrat: str, bout: str, point: float,
                 poignee: str, petit: str, pt_che: str, gd_che: str):
    """Retourne le résultat d'une donne"""
    coef = valeur_contrat(contrat)
    cible = valeur_cible(bout)
    point, signe = valeurs_donne(point, cible)
    resultat = (abs(cible - point) + 25) * coef

    if poignee:
        resultat += ajout_poignee(poignee)
    if petit:
        resultat += ajout_petit(petit, coef, signe)
    if pt_che:
        resultat += ajout_pt_chelem(signe)
    if gd_che:
        resultat += ajout_gd_chelem(gd_che, signe)

    return resultat * signe

def valeur_contrat(contrat):
    if contrat == "G":
        return 2
    elif contrat == "GS":
        return 4
    else:
        return 6

def valeur_cible(bout):
    if bout == "0":
        return 56
    elif bout == "1":
        return 51
    elif bout == "2":
        return 41
    else:
        return 36

def valeurs_donne(point, cible):
    if point < cible:
        signe = -1
        point = floor(point)
    else:
        signe = 1
        point = ceil(point)
    return point, signe

def ajout_poignee(annonce):
    if annonce == "Simple":
        return 20
    elif annonce == "Double":
        return 30
    else:
        return 40

def ajout_petit(annonce, coef, signe):
    return 10 * coef * signe if annonce == "Gagné" else -10 * coef * signe

def ajout_pt_chelem(signe):
    return 200 * signe

def ajout_gd_chelem(annonce, signe):
    if annonce == "Raté":
        return -200 * signe
    elif annonce == "Réussi ss annonce":
        return 200 * signe
    else:
        return 400 * signe
