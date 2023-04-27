from datetime import datetime

from suivi_tarot.api.data import Data
from suivi_tarot.api.utils import SUB_STATISTICS, MAIN_STATISTICS_5_PLAYERS, GENERAL_STATISTICS_5_PLAYERS, \
    MAIN_STATISTICS_3_OR_4_PLAYERS, GENERAL_STATISTICS_3_OR_4_PLAYERS


class Statistic(Data):
    def __init__(self, start_date: datetime, end_date: datetime, table_of: int):
        super().__init__(start_date=start_date, end_date=end_date, table_of=table_of)

        if self.table_of == 5:
            self.stat_formatting_5_players()
        else:
            self.stat_formatting_3_or_4_players()
        self.donne.apply(self.calculs_stat, axis=1)
        self.stat_global_informations()

    def __str__(self):
        return f"Statistiques des parties à {self.table_of} joueurs entre le {self.start_date.strftime('%d/%m/%Y')} " \
               f"et le {self.end_date.strftime('%d/%m/%Y')}."

    def __repr__(self):
        return f"Statistic(datetime({self.start_date.year}, {self.start_date.month}, {self.start_date.day}), " \
               f"datetime({self.end_date.year}, {self.end_date.month}, {self.end_date.day}), {self.table_of})"

    def stat_formatting_5_players(self):
        """Prépare le dictionnaire stockant les statistiques de parties à 5 joueurs"""

        self.stat = {player: {
            appele: {**SUB_STATISTICS} for appele in [*self.distinct_player, "Chien", "Solo"] if player != appele
        } for player in self.distinct_player}

        for player in self.distinct_player:
            self.stat[player].update(MAIN_STATISTICS_5_PLAYERS)

        self.stat["_global"] = GENERAL_STATISTICS_5_PLAYERS

    def stat_formatting_3_or_4_players(self):
        """Prépare le dictionnaire stockant les statistiques de parties à 3 ou 4 joueurs"""

        self.stat = {player: MAIN_STATISTICS_3_OR_4_PLAYERS.copy() for player in self.distinct_player}
        self.stat["_global"] = GENERAL_STATISTICS_3_OR_4_PLAYERS

    def calculs_stat(self, donne: dict):
        self.stat_preneur(donne=donne)
        if self.table_of == 5:
            self.stat_appele(donne=donne)
        self.stat_defense(donne=donne)
        self.stat_global_calcul(donne=donne)

    def stat_preneur(self, donne: dict):
        self.stat[donne["preneur"]]["preneur"] += 1
        self.stat[donne["preneur"]][donne["contract"].name] += 1
        self.stat[donne["preneur"]]["nb_donne"] += 1
        self.stat[donne["preneur"]][f"{donne['nb_bout']} bout{'s' if int(donne['nb_bout']) > 1 else ''}"] += 1
        self.stat[donne["preneur"]]["points_preneur"] += donne[donne["preneur"]]
        self.stat[donne["preneur"]]["points"] += donne[donne["preneur"]]
        if self.table_of == 5:
            self.stat[donne["preneur"]][donne["tete"]] += 1
            self.stat[donne["preneur"]][donne["appele"]][donne["contract"].name] += 1
            self.stat[donne["preneur"]][donne["appele"]][f"points_{donne['contract'].name}"] += donne[donne["preneur"]]

    def stat_appele(self, donne: dict):
        if donne["appele"] in self.distinct_player:
            self.stat[donne["appele"]]["appele"] += 1
            self.stat[donne["appele"]]["nb_donne"] += 1
            self.stat[donne["appele"]]["points_appele"] += donne[donne["appele"]]
            self.stat[donne["appele"]]["points"] += donne[donne["appele"]]

    def stat_defense(self, donne: dict):
        self.stat_defense_with_position_as_role(donne, "defense1", "defense", "nb_donne")
        self.stat_defense_with_position_as_role(donne, "defense2", "nb_donne", "defense")
        if donne["defense3"] in self.distinct_player:
            self.stat_defense_with_position_as_role(donne, "defense3", "defense", "nb_donne")
        if donne["defense4"] in self.distinct_player:
            self.stat_defense_with_position_as_role(donne, "defense4", "defense", "nb_donne")

    def stat_defense_with_position_as_role(self, donne: dict, arg1: str, arg2: str, arg3: str):
        self.stat[donne[arg1]][arg2] += 1
        self.stat[donne[arg1]][arg3] += 1
        self.stat[donne[arg1]]["points_defense"] += donne[donne[arg1]]
        self.stat[donne[arg1]]["points"] += donne[donne[arg1]]

    def stat_global_calcul(self, donne: dict):
        self.stat["_global"][donne["contract"].name] += 1
        if self.table_of == 5:
            self.stat["_global"][donne["tete"]] += 1

    def stat_global_informations(self):
        self.stat["_global"]["nb_donnes"] = self.number_of_donne
        self.stat["_global"]["nb_games"] = self.number_of_game
        self.stat["_global"]["players"] = self.distinct_player
        self.stat["_global"]["nb_players"] = len(self.distinct_player)


if __name__ == '__main__':
    from pprint import pprint as print

    nb = 5
    depart = datetime(2023, 1, 1)
    fin = datetime(2023, 3, 31)
    stat = Statistic(depart, fin, nb)

    print(stat.stat)
