from database.clients import get_joueur


def joueur_is_valid(new_joueur: str) -> bool:
    joueurs_existant = [pseudo[0] for pseudo in get_joueur()]
    longueur = len(new_joueur) > 3
    disponible = new_joueur.lower() not in [joueur.lower() for joueur in joueurs_existant]
    return all([longueur, disponible])


if __name__ == '__main__':
    print(joueur_is_valid("sirène"))
