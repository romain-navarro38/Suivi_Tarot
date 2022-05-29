from datetime import datetime
from functools import partial

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCloseEvent
from PySide6.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QHeaderView, QPushButton, QLabel, QHBoxLayout, \
    QSizePolicy, QGridLayout, QSpacerItem, QMessageBox

from suivi_tarot.api.calcul import conversion_contract, conversion_poignee
from suivi_tarot.database.clients import insert_new_game, insert_players_game, insert_donne, insert_preneur, \
    insert_appele, insert_pnj, insert_defense
from suivi_tarot.database.models import Donne
from suivi_tarot.window.graph_ranking import GraphWidget
from suivi_tarot.window.pnj import PnjWindow
from suivi_tarot.window.donne import DetailsWindow
from suivi_tarot.api.utils import HEADER_3_4, HEADER_5, HEADER_6, COLOR_GRAPH, get_random_item_with_constraint


class LabelScore(QLabel):
    number_label = 0

    def __init__(self, text, role):
        super().__init__(text)

        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        if role == "form":
            self.setAlignment(Qt.AlignRight)
        elif role == "label":
            self.setStyleSheet(f"color: {COLOR_GRAPH[self.number_label]};")
            LabelScore.number_label += 1


# noinspection PyAttributeOutsideInit
class TableWindow(QWidget):
    """Fenêtre représentant une partie où les donnes associées sont
    représentées par une ligne d'un QTableWidget"""

    refresh_graph = Signal(dict, int, str)

    def __init__(self, players):
        super().__init__()

        self.players = players
        self.pnj = list(players)
        self.number_players = len(players)
        self.score = {k: [0] for k in players}
        self.score_cumul = dict(self.score)
        self.saved = False

        self.setWindowTitle("Partie en cours")
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.tab_donne = QTableWidget(self)
        self.btn_add_row = QPushButton("Nouvelle donne")
        self.btn_valid_game = QPushButton("Valider partie")
        self.graph = GraphWidget(self)
        self.graph.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.lbl_player = [LabelScore(f"{player} :", "label") for player in self.players]
        self.lbl_score = [LabelScore("0", "form") for _ in range(self.number_players)]
        self.spacer_high = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.spacer_low = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def modify_widgets(self):
        self.tab_donne.setMinimumWidth(1200)
        header = self.select_header()
        self.tab_donne.setColumnCount(len(header))
        self.tab_donne.setHorizontalHeaderLabels(header)
        headerH = self.tab_donne.horizontalHeader()
        for i in range(self.tab_donne.columnCount()):
            headerH.setSectionResizeMode(i, QHeaderView.Stretch)

        self.new_row(0)

    def create_layouts(self):
        self.button_layout = QHBoxLayout()
        self.score_layout = QGridLayout()
        self.vertical_score_layout = QVBoxLayout()
        self.graph_score_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.tab_donne)
        self.button_layout.addWidget(self.btn_add_row)
        self.button_layout.addWidget(self.btn_valid_game)
        self.main_layout.addLayout(self.button_layout)

        self.graph_score_layout.addWidget(self.graph)
        for i in range(self.number_players):
            self.score_layout.addWidget(self.lbl_player[i], i, 0)
            self.score_layout.addWidget(self.lbl_score[i], i, 1)
        self.vertical_score_layout.addSpacerItem(self.spacer_high)
        self.vertical_score_layout.addLayout(self.score_layout)
        self.vertical_score_layout.addSpacerItem(self.spacer_high)
        self.graph_score_layout.addLayout(self.vertical_score_layout)
        self.main_layout.addLayout(self.graph_score_layout)

    def setup_connections(self):
        self.tab_donne.cellDoubleClicked.connect(self.dispatch_action)
        self.btn_add_row.clicked.connect(partial(self.dispatch_action, "add"))
        self.btn_valid_game.clicked.connect(self.valid_game)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Si la partie n'est sauvegardée, demande à l'utilisateur de confirmer l'abandon"""
        if not self.saved:
            msg = "La partie n'a pas été enregistré !\nEtes-vous sur de vouloir quitter ?"
            choice = self.popup_validation(QMessageBox.Warning, msg, QMessageBox.No)
            if choice == QMessageBox.No:
                event.ignore()

    def new_row(self, row):
        """Insére une nouvelle ligne dans QTableWidget"""
        self.tab_donne.insertRow(row)
        self.tab_donne.setRowHeight(row, 15)
        for i in range(self.tab_donne.columnCount()):
            label = QLabel("")
            label.setAlignment(Qt.AlignCenter)
            self.tab_donne.setCellWidget(row, i, label)
        if self.number_players > 5:
            self.draw_pnj(row)

    def draw_pnj(self, row):
        """Pour les sessions à 6 joueurs : tirage au sort d'un joueur qui devient
        pnj (personne non-joueur) de la donne"""
        previous_pnj = self.tab_donne.cellWidget(row - 1, 0).text() if row else ""
        new_pnj = get_random_item_with_constraint(self.pnj, previous_pnj)
        self.tab_donne.cellWidget(row, 0).setText(new_pnj)
        self.pnj.remove(new_pnj)
        if len(self.pnj) == 0:
            self.pnj = list(self.players)

    def select_header(self):
        """Retourne l'entête adapté au nombre de joueurs"""
        if self.number_players < 5:
            return HEADER_3_4
        elif self.number_players == 5:
            return HEADER_5
        return HEADER_6

    def comeback_donne(self, param_donne, row, point):
        """Récupère les infos de la fenêtre de saisi d'une donne,
        les ajoute au QTableWidget et lance les mises à jour graph et scores"""
        for column in range(self.tab_donne.columnCount()):
            self.tab_donne.cellWidget(row, column).setText(str(param_donne[column]))

        self.assign_points(param_donne, row, point)
        self.score_cumul = self.accumulate_score(self.score)
        self.refresh_graph.emit(
            self.score_cumul,
            self.tab_donne.rowCount() + 1,
            "table")
        self.display_score()

        if row == self.tab_donne.rowCount() - 1:
            self.new_row(self.tab_donne.rowCount())
            self.tab_donne.scrollToBottom()

    def dispatch_action(self, row, column=1):
        """Lance en fonction l'interaction de l'utilisateur :
            - Fenêtre pnj pour le remplacer (conditions : 6 joueurs, aucune donne jouée)
            - Fenêtre donne en mode ajout (conditions : btn_ajout_donne ou double clic dernière ligne)
            - Fenêtre donne en mode modif (condition : double clic sur une ligne renseignée)"""
        if (
                self.number_players > 5
                and self.tab_donne.rowCount() == 1
                and row == 0
                and column == 0
                and self.tab_donne.cellWidget(0, 1).text() == ""
        ):
            self.new_pnj = PnjWindow(self.pnj)
            self.new_pnj.select_player.connect(self.replace_pnj)
            self.new_pnj.setWindowModality(Qt.ApplicationModal)
            self.new_pnj.show()
        elif row == "add":
            row = self.tab_donne.rowCount() - 1
            self.value_donne = ()
            self.launch_donne(row)
        else:
            self.value_donne = self.get_value_donne(row)
            self.launch_donne(row)

    def replace_pnj(self, pnj):
        """Pour les sessions à 6 joueurs, remplace le pnj de la première donne."""
        self.tab_donne.cellWidget(0, 0).setText(pnj)
        self.pnj = list(self.players)
        self.pnj.remove(pnj)

    def launch_donne(self, row):
        """Ouvre la fenêtre de saisi d'une donne en mode création ou ajout."""
        pnj = self.tab_donne.cellWidget(row, 0).text() if self.number_players > 5 else ""
        players_donne = list(self.players)
        if pnj:
            players_donne.remove(pnj)
        self.donne = DetailsWindow(players_donne, row, self.value_donne, pnj)
        self.donne.donne_valid.connect(self.comeback_donne)
        self.donne.setWindowModality(Qt.ApplicationModal)
        self.donne.show()

    def get_value_donne(self, row):
        """Récupère les données d'une ligne du QTableWidget"""
        if self.number_players < 5:
            return (self.tab_donne.cellWidget(row, c).text() for c in range(8))
        elif self.number_players == 5:
            return (self.tab_donne.cellWidget(row, c).text() for c in range(10))
        else:
            return (self.tab_donne.cellWidget(row, c).text() for c in range(1, 11))

    def assign_points(self, param, row, point):
        """Met à jour les scores des joueurs"""
        if self.number_players > 5:
            pnj = param[0]
            preneur = param[1]
            appele = param[6]
        elif self.number_players == 5:
            pnj = [""]
            preneur = param[0]
            appele = param[5]
        else:
            pnj = [""]
            preneur = param[0]
            appele = [""]

        action = "add" if row == self.tab_donne.rowCount() - 1 else "replace"
        for player in self.players:
            if player not in [pnj, preneur, appele]:
                liste = self.add_or_replace_value_list(action, self.score[player], point[2], row + 1)
            elif player == pnj:
                liste = self.add_or_replace_value_list(action, self.score[player], "0", row + 1)
            elif player == preneur:
                liste = self.add_or_replace_value_list(action, self.score[player], point[0], row + 1)
            else:
                liste = self.add_or_replace_value_list(action, self.score[player], point[1], row + 1)

            self.score[player] = liste

    @staticmethod
    def add_or_replace_value_list(choice: str, list_score: list[int], value: str, index_: int) -> list[int]:
        """Retourne une liste de score après lui avoir ajouté ou modifié une valeur"""
        value = int(value)
        if choice == "add":
            list_score.append(value)
        else:
            list_score[index_] = value
        return list_score

    @staticmethod
    def accumulate_score(score: dict) -> dict:
        """Retourne un dictionnaire où la clé est un joueur et
        la valeur une liste de ses scores cumulés au fur et à mesure des donnes"""
        cumul_dict = {}
        for player, values in score.items():
            cumul = 0
            cumul_liste = []
            for value in values:
                cumul += value
                cumul_liste.append(cumul)
            cumul_dict[player] = cumul_liste
        return cumul_dict

    def display_score(self):
        """Met à jour les labels score de chaque joueur puis les déplacent
        dans le grid layout pour les mettre en selection_order décroissant"""
        for i, liste in enumerate(self.score_cumul.values()):
            self.lbl_score[i].setText(str(liste[-1]))

        liste = [(self.score_layout.itemAtPosition(i, 0).widget(),
                  int(self.score_layout.itemAtPosition(i, 1).widget().text()),
                  self.score_layout.itemAtPosition(i, 1).widget())
                 for i in range(self.number_players)]
        classement = sorted(liste, key=lambda v: v[1], reverse=True)

        for i in range(self.number_players):
            self.score_layout.addWidget(classement[i][0], i, 0)
            self.score_layout.addWidget(classement[i][2], i, 1)

    def valid_game(self):
        """Enregistre en bdd la partie et donnes associées"""
        if self.tab_donne.rowCount() <= 2:
            return

        choice = self.popup_validation(QMessageBox.Question, "Terminer la partie ?", QMessageBox.Yes)
        if choice == QMessageBox.Yes:
            game_id = self.save_game()
            self.save_players(game_id)
            for row in range(self.tab_donne.rowCount() - 1):
                donne_id = self.save_donne(game_id, row)
                self.save_preneur(donne_id)
                self.save_appele(donne_id)
                self.save_pnj(donne_id)
                self.save_defense(donne_id)
            self.saved = True
            self.close()

    def save_game(self) -> int:
        """Enregistre la partie, soit la date et le type de jeu (à 3, 4 ou 5 joueurs).
        Retourne l'id de la partie ainsi enregistrée"""
        partie = {"date_": datetime.now(),
                  "table_": self.number_players if self.number_players < 6 else 5}
        return insert_new_game(**partie)

    def save_players(self, partie_id: int):
        """Enregistre les joueurs participants"""
        insert_players_game(partie_id, self.players)

    def save_donne(self, game_id: int, row: int) -> int:
        """Enregistre une donne de la partie et retourne son id généré"""
        column = ["preneur", "contrat", "nb_bout", "point", "poignee", "petit", "petit_chelem", "grand_chelem"]
        if self.number_players > 4:
            column.insert(4, "tete")
            column.insert(5, "appele")

        liste = list(self.get_value_donne(row))
        self.dict_donne = dict(zip(column, liste))
        if self.number_players < 5:
            self.dict_donne["tete"] = None
            self.dict_donne["appele"] = None
        if self.number_players == 6:
            self.dict_donne["pnj"] = self.tab_donne.cellWidget(row, 0).text()
        else:
            self.dict_donne["pnj"] = None
        donne = Donne(game_id=game_id,
                      nb_bout=int(self.dict_donne["nb_bout"]),
                      contract=conversion_contract(self.dict_donne["contrat"]),
                      tete=self.dict_donne["tete"],
                      point=float(self.dict_donne["point"]),
                      petit=self.dict_donne["petit"],
                      poignee=conversion_poignee(self.dict_donne["poignee"]),
                      petit_chelem=self.dict_donne["petit_chelem"],
                      grand_chelem=self.dict_donne["grand_chelem"])
        return insert_donne(donne)

    def save_preneur(self, donne_id: int):
        """Enregistre le preneur d'une donne"""
        insert_preneur(donne_id, self.dict_donne["preneur"])

    def save_appele(self, donne_id: int):
        """Enregistre l'appelé d'une donne (partie à 5 ou 6 joueurs)"""
        if self.dict_donne["appele"]:
            insert_appele(donne_id, self.dict_donne["appele"])

    def save_pnj(self, donne_id: int):
        """Enregistre le joueur n'ayant pas joué la donne (partie à 6 joueurs)"""
        if self.dict_donne["pnj"]:
            insert_pnj(donne_id, self.dict_donne["pnj"])

    def save_defense(self, donne_id: int):
        """Enregistre les joueurs ayant joué en défense une donne"""
        defense = list(self.players)
        for player in self.players:
            if player in (self.dict_donne.get("preneur", ""),
                          self.dict_donne.get("appele", ""),
                          self.dict_donne.get("pnj", "")):
                defense.remove(player)

        for number, player in enumerate(defense, 1):
            insert_defense(donne_id, player, number)

    @staticmethod
    def popup_validation(icon: QMessageBox.Icon, text: str, default_btn: QMessageBox.StandardButton):
        """Demande une confirmation oui non à l'utilisateur via un pop-up"""
        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setIcon(icon)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(default_btn)
        msg.show()
        return msg.exec()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from suivi_tarot.api.utils import PLAYERS

    app = QApplication()
    window = TableWindow(PLAYERS)
    window.show()
    app.exec()
