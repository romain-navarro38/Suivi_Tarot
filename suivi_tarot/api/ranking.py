from datetime import datetime

import pandas as pd

from suivi_tarot.database.clients import get_donne, get_preneur, get_appele, get_defense, get_pnj, get_distinct_player
from suivi_tarot.api.calcul import calcul_donne, repartition_points_by_player


# noinspection PyAttributeOutsideInit
class Ranking:
    """Récupération et traitement des données relativent aux parties jouées pour un
    interval de temps et un nombre de joueurs autour de la table."""
    def __init__(self, start_date: datetime, end_date: datetime, table_of: int):
        self.start_date = start_date
        self.end_date = end_date
        self.table_of = table_of
        self.data_extraction()
        self.data_processing()

    def data_extraction(self):
        """Récupération des donnes et des différents joueurs associés dans leurs rôles"""
        self.distinct_player = get_distinct_player(self.start_date, self.end_date, self.table_of)
        self.donne_extraction()
        self.preneur_extraction()
        self.appele_extraction()
        self.defense_extraction()
        self.pnj_extraction()

    def data_processing(self):
        """Traitement des données"""
        self.calcul_base_donne()
        self.cumul = pd.DataFrame()
        self.distribution_of_points()
        self.cumulative_points_per_game()

    def donne_extraction(self):
        """Récupère chaque donne"""
        self.donne = get_donne(self.start_date, self.end_date, self.table_of)

    def preneur_extraction(self):
        """Récupère et ajoute à chaque donne le preneur associé"""
        self.donne["preneur"] = get_preneur(self.start_date, self.end_date, self.table_of)

    def appele_extraction(self):
        """Récupère et ajoute à chaque donne l'appelé associé. Valable seulement pour
        les tables de 5 (joués avec 5 ou 6 joueurs)"""
        self.donne["appele"] = get_appele(self.start_date, self.end_date, self.table_of)

    def defense_extraction(self):
        """Récupère et ajoute à chaque donne les défenseurs associés"""
        for i in range(1, 5):
            self.donne[f"defense{i}"] = get_defense(self.start_date, self.end_date, self.table_of, i)

    def pnj_extraction(self):
        """Récupère et ajoute à chaque donne le pnj associé. Valable seulement pour
        les tables de 5 joués à 6 joueurs (un joueur différent ne joue pas à chaque donne)"""
        self.donne["pnj"] = get_pnj(self.start_date, self.end_date, self.table_of)

    def calcul_base_donne(self):
        """Calcul pour chaque donne le résultat"""
        param_calcul = [calcul_donne(row["contract"],
                                     str(row["nb_bout"]),
                                     row["point"],
                                     row["poignee"],
                                     row["petit"],
                                     row["petit_chelem"],
                                     row["grand_chelem"])
                        for index_, row in self.donne.iterrows()]
        self.donne["result"] = param_calcul

    def distribution_of_points(self):
        """Ajoute une colonne pour chaque joueur au DataFrame donne et calcul les points
        du joueur pour chaque donne"""
        for player in self.distinct_player:
            self.donne[player] = self.donne.apply(repartition_points_by_player, axis=1, player=player)
            self.cumul[player] = self.donne[player]

    def cumulative_points_per_game(self):
        """Création d'un DataFrame représentant le cumul des scores de chaque joueur
        par partie"""
        self.cumul['id_game'] = self.donne['id_game']
        self.cumul.reset_index(inplace=True, drop=True)
        self.cumul = self.cumul.groupby('id_game').sum()
        self.ranking: pd.DataFrame = self.cumul.cumsum()
        self.ranking.reset_index(inplace=True, drop=True)

    @property
    def number_of_game(self) -> int:
        """Nombre de parties trouvées"""
        return self.ranking.shape[0]


if __name__ == '__main__':
    nb = 4
    depart = datetime(2022, 1, 1)
    fin = datetime(2022, 3, 31)
    rank = Ranking(depart, fin, nb)
    with pd.option_context("display.max_columns", None):
        print(rank.ranking)
    print(rank.number_of_game)
