from enum import Enum, auto

from suivi_tarot.database.clients import get_all_players


class Comparison(Enum):
    """Enumération des opérateurs de comparaison"""
    EQUAL = auto()
    DIFFERENT = auto()
    GREATER_THAN = auto()
    LESS_THAN = auto()
    GREATER_THAN_OR_EQUAL = auto()
    LESS_THAN_OR_EQUAL = auto()


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


if __name__ == '__main__':
    print(check_length_str("ee", 2, Comparison.EQUAL))
