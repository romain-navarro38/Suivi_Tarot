from datetime import datetime

import pandas as pd

from suivi_tarot.api.data import Data


class Statistic(Data):
    def __init__(self, start_date: datetime, end_date: datetime, table_of: int):
        super().__init__(start_date=start_date, end_date=end_date, table_of=table_of)

    @property
    def number_of_donne(self) -> int:
        """Nombre de donnes trouvées"""
        return self.donne.shape[0]


if __name__ == '__main__':
    nb = 5
    depart = datetime(2023, 1, 1)
    fin = datetime(2023, 3, 31)
    stat = Statistic(depart, fin, nb)
    # with pd.option_context("display.max_columns", None):
    #     print(stat.donne)
    print(stat.number_of_donne)
