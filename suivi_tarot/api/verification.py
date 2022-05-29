from enum import Enum
from pathlib import Path

from suivi_tarot.api.utils import hashage_password
from suivi_tarot.database.clients import get_all_players, get_hash_and_salt


class Comparison(Enum):
    """Enumération des opérateurs de comparaison"""
    EQUAL = 1
    DIFFERENT = 2
    GREATER_THAN = 3
    LESS_THAN = 4
    GREATER_THAN_OR_EQUAL = 5
    LESS_THAN_OR_EQUAL = 6


def player_is_valid(new_player: str) -> bool:
    """Vérifie si un pseudo respecte les conditions"""
    length = check_length_str(new_player, 3, Comparison.GREATER_THAN)
    available = check_availability_nickname(new_player)
    return all([length, available])


def check_availability_nickname(new_player: str) -> bool:
    """Vérifie si le pseudo est disponible dans la bdd
    (non sensible à la casse)"""
    existing_players = get_all_players()
    return new_player.lower() not in [player.lower() for player in existing_players]


def check_length_str(text: str, target: int, comparison: Comparison) -> bool:
    """Compare la longueur d'une chaîne de caractères à une cible en fonction
    d'un opérateur de comparaison"""
    match comparison:
        case Comparison.EQUAL:
            return len(text) == target
        case Comparison.DIFFERENT:
            return len(text) != target
        case Comparison.GREATER_THAN:
            return len(text) > target
        case Comparison.LESS_THAN:
            return len(text) < target
        case Comparison.GREATER_THAN_OR_EQUAL:
            return len(text) >= target
        case Comparison.LESS_THAN_OR_EQUAL:
            return len(text) <= target


def path_is_existing_folder_or_file(path: str, type_: str) -> bool:
    """Vérifie si un chemin et bien un dossier ou un fichier"""
    return Path(path).is_dir() if type_ == "folder" else Path(path).is_file()


def check_password(password: str) -> bool:
    """Contrôle du mot de passe"""
    hash_, salt = get_hash_and_salt()
    password_hash, _ = hashage_password(password, salt)
    if password_hash == hash_:
        return True
    return False


if __name__ == '__main__':
    print(path_is_existing_folder_or_file(r"C:\Users\Romain\Projet\Suivi_Tarot\config.json", "file"))
