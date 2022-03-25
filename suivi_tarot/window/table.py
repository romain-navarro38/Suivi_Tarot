from datetime import datetime
from random import choice
from functools import partial

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCloseEvent
from PySide6.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QHeaderView, QPushButton, QLabel, QHBoxLayout, \
    QSizePolicy, QGridLayout, QSpacerItem, QMessageBox

from api.calcul import conversion_contrat, conversion_poignee
from database.clients import insert_new_partie, insert_joueurs_partie, insert_donne, insert_preneur, insert_appele, \
    insert_pnj, insert_defense
from database.models import Donne
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
    """Fenêtre représentant une partie où les donnes associées sont
    représentées par une ligne d'un QTableWidget"""

    refresh_graph = Signal(dict, int)

    def __init__(self, joueurs):
        super().__init__()

        self.joueurs = joueurs
        self.pnj = list(joueurs)
        self.nombre_joueurs = len(joueurs)
        self.score = {k: [0] for k in joueurs}
        self.score_cumul = dict(self.score)
        self.saved = False

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
        self.btn_valid_session.clicked.connect(self.valid_partie)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Si la partie n'est sauvegardée, demande à l'utilisateur de confirmer l'abandon"""
        if not self.saved:
            msg = "La partie n'a pas été enregistré !\nEtes-vous sur de vouloir quitter ?"
            choix = self.popup_validation(QMessageBox.Warning, msg, QMessageBox.No)
            if choix == QMessageBox.No:
                event.ignore()

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
        """Retourne un dictionnaire où la clé est un joueur et
        la valeur une liste de ses scores cumulés au fur et à mesure des donnes"""
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

    def valid_partie(self):
        """Enregistre en bdd la partie et donnes associées"""
        if self.tab_donne.rowCount() <= 2:
            return

        choix = self.popup_validation(QMessageBox.Question, "Terminer la partie ?", QMessageBox.Yes)
        if choix == QMessageBox.Yes:
            partie_id = self.save_partie()
            self.save_joueurs(partie_id)
            for row in range(self.tab_donne.rowCount() - 1):
                donne_id = self.save_donne(partie_id, row)
                self.save_preneur(donne_id)
                self.save_appele(donne_id)
                self.save_pnj(donne_id)
                self.save_defense(donne_id)
            self.saved = True
            self.close()

    def save_partie(self) -> int:
        """Enregistre la partie, soit la date et le type de jeu (à 3, 4 ou 5 joueurs).
        Retourne l'id de la partie ainsi enregistrée"""
        partie = {"date_": datetime.now(),
                  "table_": self.nombre_joueurs if self.nombre_joueurs < 6 else 5}
        return insert_new_partie(**partie)

    def save_joueurs(self, partie_id: int):
        """Enregistre les joueurs participants"""
        insert_joueurs_partie(partie_id, self.joueurs)

    def save_donne(self, partie_id: int, row: int) -> int:
        """Enregistre une donne de la partie et retourne son id généré"""
        column = ["preneur", "contrat", "nb_bout", "point", "poignee", "petit", "pt_chelem", "gd_chelem"]
        if self.nombre_joueurs > 4:
            column.insert(4, "tete")
            column.insert(5, "appele")

        liste = list(self.get_valeur_donne(row))
        self.dict_donne = dict(zip(column, liste))
        if self.nombre_joueurs < 5:
            self.dict_donne["tete"] = None
            self.dict_donne["appele"] = None
        if self.nombre_joueurs == 6:
            self.dict_donne["pnj"] = self.tab_donne.cellWidget(row, 0).text()
        else:
            self.dict_donne["pnj"] = None
        donne = Donne(partie_id=partie_id,
                      nb_bout=int(self.dict_donne["nb_bout"]),
                      contrat=conversion_contrat(self.dict_donne["contrat"]),
                      tete=self.dict_donne["tete"],
                      point=float(self.dict_donne["point"]),
                      petit=self.dict_donne["petit"],
                      poignee=conversion_poignee(self.dict_donne["poignee"]),
                      pt_chelem=self.dict_donne["pt_chelem"],
                      gd_chelem=self.dict_donne["gd_chelem"])
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
        defense = list(self.joueurs)
        for joueur in self.joueurs:
            if joueur in (self.dict_donne.get("preneur", ""),
                          self.dict_donne.get("appele", ""),
                          self.dict_donne.get("pnj", "")):
                defense.remove(joueur)

        for numero, joueur in enumerate(defense, 1):
            insert_defense(donne_id, joueur, numero)

    @staticmethod
    def popup_validation(icon: QMessageBox.Icon, text: str, defaut_btn: QMessageBox.StandardButton):
        """Demande une confirmation oui non à l'utilisateur via un pop-up"""
        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setIcon(icon)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(defaut_btn)
        msg.show()
        return msg.exec()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    window = TableWindow(["Romain", "Ludovic", "Emeline", "Eddy", "Aurore"])
    window.show()
    app.exec()
