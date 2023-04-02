from datetime import datetime

import pandas as pd

from suivi_tarot.api.data import Data


# noinspection PyAttributeOutsideInit
class Ranking(Data):
    """Récupération et traitement des données relativent aux parties jouées pour un
    interval de temps et un nombre de joueurs autour de la table."""
    def __init__(self, start_date: datetime, end_date: datetime, table_of: int):
        super().__init__(start_date, end_date, table_of)

        self.ranking: pd.DataFrame = self.cumul.cumsum()
        self.ranking.reset_index(inplace=True, drop=True)

    @property
    def number_of_game(self) -> int:
        """Nombre de parties trouvées"""
        return self.ranking.shape[0]


if __name__ == '__main__':
    nb = 5
    depart = datetime(2023, 1, 1)
    fin = datetime(2023, 3, 31)
    rank = Ranking(depart, fin, nb)
    with pd.option_context("display.max_columns", None):
        print(rank.donne)
    print(rank.donne.shape[0])
