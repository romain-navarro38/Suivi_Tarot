import datetime as dt
from random import choice
from functools import partial

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QHeaderView, QPushButton, QLabel, QHBoxLayout, \
    QSizePolicy, QGridLayout, QSpacerItem

from database.clients import ajout_session
from window.graph_session import GraphSession
from window.pnj import PnjWindow
from window.donne import DetailsWindow
from api.utils import EN_TETE_3_4, EN_TETE_5, EN_TETE_6, COLOR_GRAPH


class LabelScore(QLabel):

    nombre_label = 0

    def __init__(self, text, role):
        super().__init__(text)

        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        if role == "form":
            self.setAlignment(Qt.AlignRight)
        elif role == "label":
            self.setStyleSheet(f"color: {COLOR_GRAPH[self.nombre_label]};")
            LabelScore.nombre_label += 1


# noinspection PyAttributeOutsideInit
class TableWindow(QWidget):
    """Fenêtre représentant une session où les donnes associées sont
    représentées par une ligne d'un QTableWidget"""

    refresh_graph = Signal(dict, int)

    def __init__(self, joueurs):
        super().__init__()

        self.joueurs = joueurs
        self.pnj = list(joueurs)
        self.nombre_joueurs = len(joueurs)
        self.score = {k: [0] for k in joueurs}
        self.score_cumul = dict(self.score)

        self.setWindowTitle("Session en cours")
        LabelScore.nombre_label = 0
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.tab_donne = QTableWidget(self)
        self.btn_ajout_ligne = QPushButton("Nouvelle donne")
        self.btn_valid_session = QPushButton("Valider session")
        self.graph = GraphSession(self)
        self.graph.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.lbl_joueur = [LabelScore(f"{joueur} :", "label") for joueur in self.joueurs]
        self.lbl_score = [LabelScore("0", "form") for _ in range(self.nombre_joueurs)]
        self.spacer_haut = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.spacer_bas = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def modify_widgets(self):
        self.tab_donne.setMinimumWidth(1200)
        entete = self.affichage_entete()
        self.tab_donne.setColumnCount(len(entete))
        self.tab_donne.setHorizontalHeaderLabels(entete)
        headerH = self.tab_donne.horizontalHeader()
        for i in range(self.tab_donne.columnCount()):
            headerH.setSectionResizeMode(i, QHeaderView.Stretch)

        self.new_ligne(0)

    def create_layouts(self):
        self.bouton_layout = QHBoxLayout()
        self.score_layout = QGridLayout()
        self.vertical_score_layout = QVBoxLayout()
        self.graph_score_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.tab_donne)
        self.bouton_layout.addWidget(self.btn_ajout_ligne)
        self.bouton_layout.addWidget(self.btn_valid_session)
        self.main_layout.addLayout(self.bouton_layout)

        self.graph_score_layout.addWidget(self.graph)
        for i in range(self.nombre_joueurs):
            self.score_layout.addWidget(self.lbl_joueur[i], i, 0)
            self.score_layout.addWidget(self.lbl_score[i], i, 1)
        self.vertical_score_layout.addSpacerItem(self.spacer_haut)
        self.vertical_score_layout.addLayout(self.score_layout)
        self.vertical_score_layout.addSpacerItem(self.spacer_haut)
        self.graph_score_layout.addLayout(self.vertical_score_layout)
        self.main_layout.addLayout(self.graph_score_layout)

    def setup_connections(self):
        self.tab_donne.cellDoubleClicked.connect(self.dispatch_action)
        self.btn_ajout_ligne.clicked.connect(partial(self.dispatch_action, "ajout"))
        self.btn_valid_session.clicked.connect(self.valid_session)

    def new_ligne(self, row):
        """Insére une nouvelle ligne dans QTableWidget"""
        self.tab_donne.insertRow(row)
        self.tab_donne.setRowHeight(row, 15)
        for i in range(self.tab_donne.columnCount()):
            label = QLabel("")
            label.setAlignment(Qt.AlignCenter)
            self.tab_donne.setCellWidget(row, i, label)
        if self.nombre_joueurs > 5:
            self.tirage_pnj(row)

    def tirage_pnj(self, row):
        """Pour les sessions à 6 joueurs : tirage au sort d'un joueur qui devient
        pnj (personne non-joueur) de la donne"""
        pnj = self.pnj.pop(self.pnj.index(choice(self.pnj)))
        self.tab_donne.cellWidget(row, 0).setText(pnj)
        if len(self.pnj) == 0:
            self.pnj = list(self.joueurs)

    def affichage_entete(self):
        """Retourne l'entête adapté au nombre de joueurs"""
        if self.nombre_joueurs < 5:
            return EN_TETE_3_4
        elif self.nombre_joueurs == 5:
            return EN_TETE_5
        return EN_TETE_6

    def retour_donne(self, param_donne, row, point):
        """Récupère les infos de la fenêtre de saisi d'une donne,
        les ajoute au QTableWidget et lance les mises à jour graph et scores"""
        for column in range(self.tab_donne.columnCount()):
            self.tab_donne.cellWidget(row, column).setText(
                str(param_donne[column]))

        self.attibution_points(param_donne, row, point)
        self.score_cumul = self.cumuler_score(self.score)
        self.refresh_graph.emit(
            self.score_cumul,
            self.tab_donne.rowCount() + 1)
        self.affichage_score()

        if row == self.tab_donne.rowCount() - 1:
            self.new_ligne(self.tab_donne.rowCount())
            self.tab_donne.scrollToBottom()

    def dispatch_action(self, row, column=1):
        """Lance en fonction l'interaction de l'utilisateur :
            - Fenêtre pnj pour le remplacer (conditions : 6 joueurs, aucune donne jouée)
            - Fenêtre donne en mode ajout (conditions : btn_ajout_donne ou double clic dernière ligne)
            - Fenêtre donne en mode modif (condition : double clic sur une ligne renseignée)"""
        if (
            self.nombre_joueurs > 5
            and self.tab_donne.rowCount() == 1
            and row == 0
            and column == 0
            and self.tab_donne.cellWidget(0, 1).text() == ""
        ):
            self.new_pnj = PnjWindow(self.pnj)
            self.new_pnj.select_joueur.connect(self.remplace_pnj)
            self.new_pnj.setWindowModality(Qt.ApplicationModal)
            self.new_pnj.show()
        elif row == "ajout":
            row = self.tab_donne.rowCount() - 1
            self.valeur_donne = ()
            self.lancement_donne(row)
        else:
            self.valeur_donne = self.get_valeur_donne(row)
            self.lancement_donne(row)

    def remplace_pnj(self, pnj):
        """Pour les sessions à 6 joueurs, remplace le pnj de la première donne."""
        self.tab_donne.cellWidget(0, 0).setText(pnj)
        self.pnj = list(self.joueurs)
        self.pnj.remove(pnj)

    def lancement_donne(self, row):
        """Ouvre la fenêtre de saisi d'une donne en mode création ou ajout."""
        pnj = self.tab_donne.cellWidget(row, 0).text() if self.nombre_joueurs > 5 else ""
        joueurs_donne = list(self.joueurs)
        if pnj:
            joueurs_donne.remove(pnj)
        self.donne = DetailsWindow(joueurs_donne, row, self.valeur_donne, pnj)
        self.donne.donne_valid.connect(self.retour_donne)
        self.donne.setWindowModality(Qt.ApplicationModal)
        self.donne.show()

    def get_valeur_donne(self, row):
        """Récupère les données d'une ligne du QTableWidget"""
        if self.nombre_joueurs < 5:
            return (self.tab_donne.cellWidget(row, c).text() for c in range(8))
        elif self.nombre_joueurs == 5:
            return (self.tab_donne.cellWidget(row, c).text() for c in range(10))
        else:
            return (self.tab_donne.cellWidget(row, c).text() for c in range(1, 11))

    def attibution_points(self, param, row, point):
        """Met à jour les scores des joueurs"""
        if self.nombre_joueurs > 5:
            pnj = param[0]
            preneur = param[1]
            appele = param[6]
        elif self.nombre_joueurs == 5:
            pnj = [""]
            preneur = param[0]
            appele = param[5]
        else:
            pnj = [""]
            preneur = param[0]
            appele = [""]

        action = "ajout" if row == self.tab_donne.rowCount() - 1 else "remplacement"
        for joueur in self.joueurs:
            if joueur not in [pnj, preneur, appele]:
                liste = self.ajouter_remplacer_val_liste(
                    action, self.score[joueur], point[2], row + 1)
            elif joueur == pnj:
                liste = self.ajouter_remplacer_val_liste(
                    action, self.score[joueur], "0", row + 1)
            elif joueur == preneur:
                liste = self.ajouter_remplacer_val_liste(
                    action, self.score[joueur], point[0], row + 1)
            else:
                liste = self.ajouter_remplacer_val_liste(
                    action, self.score[joueur], point[1], row + 1)

            self.score[joueur] = liste

    @staticmethod
    def ajouter_remplacer_val_liste(choix: str, liste: list[int], valeur: str, index_: int) -> list[int]:
        """Retourne une liste de score après lui avoir ajouté ou modifié une valeur"""
        valeur = int(valeur)
        if choix == "ajout":
            liste.append(valeur)
        else:
            liste[index_] = valeur
        return liste

    @staticmethod
    def cumuler_score(score: dict) -> dict:
        """Retourne un dictionnaire"""
        cumul_dict = {}
        for joueur, valeurs in score.items():
            cumul = 0
            cumul_liste = []
            for valeur in valeurs:
                cumul += valeur
                cumul_liste.append(cumul)
            cumul_dict[joueur] = cumul_liste
        return cumul_dict

    def affichage_score(self):
        """Met à jour les labels score de chaque joueur puis les déplacent
        dans le grid layout pour les mettre en selection_order décroissant"""
        for i, liste in enumerate(self.score_cumul.values()):
            self.lbl_score[i].setText(str(liste[-1]))

        liste = [(self.score_layout.itemAtPosition(i, 0).widget(),
                  int(self.score_layout.itemAtPosition(i, 1).widget().text()),
                  self.score_layout.itemAtPosition(i, 1).widget())
                 for i in range(self.nombre_joueurs)]
        classement = sorted(liste, key=lambda v: v[1], reverse=True)

        for i in range(self.nombre_joueurs):
            self.score_layout.addWidget(classement[i][0], i, 0)
            self.score_layout.addWidget(classement[i][2], i, 1)

    def valid_session(self):
        """Enregistre en bdd la session et donnes associées"""
        if self.tab_donne.rowCount() <= 2:
            return
        session = {"date_": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                   "table_": self.nombre_joueurs if self.nombre_joueurs < 6 else 5,
                   "joueurs": self.joueurs,
                   "nb_donne": self.tab_donne.rowCount() - 1}

        column = ["preneur", "contrat", "nb_bout", "point", "poignee", "petit", "pt_chelem", "gd_chelem"]
        if self.nombre_joueurs > 4:
            column.insert(4, "tete")
            column.insert(5, "appele")

        for i, row in enumerate(list(range(self.tab_donne.rowCount() - 1))):
            liste = list(self.get_valeur_donne(row))
            dict_donne = dict(zip(column, liste))
            if self.nombre_joueurs < 5:
                dict_donne["tete"] = ""
            if self.nombre_joueurs == 6:
                dict_donne["pnj"] = self.tab_donne.cellWidget(row, 0).text()
            session[f"d{i}"] = dict_donne

            defense = list(self.joueurs)
            for joueur in self.joueurs:
                if joueur in (session.get(f"d{i}").get("preneur", ""),
                              session.get(f"d{i}").get("appele", ""),
                              session.get(f"d{i}").get("pnj", "")):
                    defense.remove(joueur)
            session[f"d{i}"]["defense"] = defense

        ajout_session(**session)
        self.close()
