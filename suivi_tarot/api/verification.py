from database.clients import get_all_joueur


def joueur_is_valid(new_joueur: str) -> bool:
    """Vérification si le pseudo à longueur supérieure à 3 et s'il n'existe
    pas déjà en bdd (non sensible à la casse)"""
    joueurs_existant = get_all_joueur()
    longueur = len(new_joueur) > 3
    disponible = new_joueur.lower() not in [joueur.lower() for joueur in joueurs_existant]
    return all([longueur, disponible])


if __name__ == '__main__':
    print(joueur_is_valid("sirène"))
