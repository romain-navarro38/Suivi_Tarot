from PySide6.QtGui import QRegularExpressionValidator, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QLineEdit, QComboBox, \
    QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt, QSize, Signal

from api.utils import TETE
from api.calcul import calcul_donne, point_preneur_float


# noinspection PyAttributeOutsideInit
class DetailsWindow(QWidget):
    """Fenêtre permettant la création ou la modification d'une donne
    pour la session en cours"""

    donne_valid = Signal(list, int, list)

    def __init__(self, joueurs: list[str], ligne: int, modif: tuple, pnj: str):
        super().__init__()

        self.joueurs = joueurs
        self.nb_joueurs = len(joueurs)
        self.ligne_donne = ligne
        self.pnj = pnj
        self.modif = list(modif)
        self.point_de_lattaque = True
        self.setup_ui()
        self.resize(505, 192)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        if self.modif:
            self.affichage_modif()

    def create_widgets(self):
        self.gb_principal = QGroupBox(self)
        self.lbl_preneur = QLabel(self.gb_principal)
        self.cbx_preneur = QComboBox(self.gb_principal)
        self.lbl_contrat = QLabel(self.gb_principal)
        self.cbx_contrat = QComboBox(self.gb_principal)
        self.lbl_bout = QLabel(self.gb_principal)
        self.cbx_bout = QComboBox(self.gb_principal)
        self.lbl_point = QLabel(self.gb_principal)
        self.le_point = QLineEdit(self.gb_principal)
        self.btn_attaque_def = QPushButton(self.gb_principal)
        self.lbl_tete = QLabel(self.gb_principal)
        self.cbx_tete = QComboBox(self.gb_principal)
        self.lbl_appele = QLabel(self.gb_principal)
        self.cbx_appele = QComboBox(self.gb_principal)

        self.gb_bonus_malus = QGroupBox(self)
        self.lbl_poignee = QLabel(self.gb_bonus_malus)
        self.cbx_poignee = QComboBox(self.gb_bonus_malus)
        self.lbl_petit = QLabel(self.gb_bonus_malus)
        self.cbx_petit = QComboBox(self.gb_bonus_malus)
        self.lbl_pt_chelem = QLabel(self.gb_bonus_malus)
        self.cbx_pt_chelem = QComboBox(self.gb_bonus_malus)
        self.lbl_gd_chelem = QLabel(self.gb_bonus_malus)
        self.cbx_gd_chelem = QComboBox(self.gb_bonus_malus)

        self.spacer_sep = QSpacerItem(378, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.spacer_gauche = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.lbl_point_preneur = QLabel("Preneur")
        self.lbl_result_preneur = QLabel("")
        self.lbl_point_appele = QLabel("Appelé")
        self.lbl_result_appele = QLabel("")
        self.lbl_point_defense = QLabel("Défense")
        self.lbl_result_defense = QLabel("")
        self.spacer_milieu = QSpacerItem(1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.btn_valider = QPushButton("Valider")
        self.btn_annuler = QPushButton("Annuler")
        self.spacer_droite = QSpacerItem(2, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.lbl_pnj = QLabel("")

    def modify_widgets(self):
        self.lbl_preneur.setAlignment(Qt.AlignCenter)
        self.lbl_preneur.setText("Preneur")
        self.fill_cbx_preneur_appele(self.joueurs, self.joueurs)
        self.cbx_preneur.setCurrentIndex(-1)
        self.lbl_contrat.setAlignment(Qt.AlignCenter)
        self.lbl_contrat.setText("Contrat")
        self.cbx_contrat.addItems(["G", "GS", "GC"])
        self.cbx_contrat.setCurrentIndex(-1)
        self.lbl_bout.setAlignment(Qt.AlignCenter)
        self.lbl_bout.setText("Bout")
        self.cbx_bout.addItems(["0", "1", "2", "3"])
        self.cbx_bout.setCurrentIndex(-1)
        self.lbl_point.setAlignment(Qt.AlignCenter)
        self.lbl_point.setText("Point")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.le_point.sizePolicy().hasHeightForWidth())
        self.le_point.setSizePolicy(sizePolicy)
        self.le_point.setMaximumSize(QSize(32, 16777215))
        self.le_point.setAlignment(Qt.AlignCenter)
        self.le_point.setPlaceholderText("0")
        # regex acceptant seulement les nombres entre 0 et 91 par pas de 0.5 ('.' ou ',' accepté)
        pointValidator = QRegularExpressionValidator()
        pointValidator.setRegularExpression(r"(([0-8]?\d?((\.|,)[5])?)|([9][0]((\.|,)[5])?)|[9][1])")
        self.le_point.setValidator(pointValidator)
        self.btn_attaque_def.setMaximumSize(QSize(40, 16777215))
        self.btn_attaque_def.setText("Att")
        if self.nb_joueurs > 4:
            self.lbl_tete.setAlignment(Qt.AlignCenter)
            self.lbl_tete.setText("Tête")
            self.cbx_tete.addItems(TETE)
            self.cbx_tete.setCurrentIndex(-1)
            self.lbl_appele.setAlignment(Qt.AlignCenter)
            self.lbl_appele.setText("Appelé")
            self.cbx_appele.setCurrentIndex(-1)
        else:
            self.lbl_tete.setVisible(False)
            self.cbx_tete.setVisible(False)
            self.lbl_appele.setVisible(False)
            self.cbx_appele.setVisible(False)
        self.gb_principal.setTitle("Principal")

        self.lbl_poignee.setAlignment(Qt.AlignCenter)
        self.lbl_poignee.setText("Poignée")
        self.cbx_poignee.addItems(["", "Simple", "Double", "Triple"])
        self.cbx_poignee.setCurrentIndex(-1)
        self.lbl_petit.setAlignment(Qt.AlignCenter)
        self.lbl_petit.setText("Petit au bout")
        self.cbx_petit.addItems(["", "Gagné", "Perdu"])
        self.cbx_petit.setCurrentIndex(-1)
        self.lbl_pt_chelem.setAlignment(Qt.AlignCenter)
        self.lbl_pt_chelem.setText("Petit chelem")
        self.cbx_pt_chelem.addItems(["", "Oui"])
        self.cbx_pt_chelem.setCurrentIndex(-1)
        self.lbl_gd_chelem.setAlignment(Qt.AlignCenter)
        self.lbl_gd_chelem.setText("Grand chelem")
        self.cbx_gd_chelem.addItems(["", "Réussi", "Réussi ss annonce", "Raté"])
        self.cbx_gd_chelem.setCurrentIndex(-1)
        self.gb_bonus_malus.setTitle("Bonus / Malus")

        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        size = QSize(64, 32)
        self.lbl_point_preneur.setAlignment(Qt.AlignCenter)
        self.lbl_result_preneur.setFont(font)
        self.lbl_result_preneur.setMinimumSize(size)
        self.lbl_result_preneur.setAlignment(Qt.AlignCenter)
        self.lbl_point_appele.setAlignment(Qt.AlignCenter)
        self.lbl_result_appele.setFont(font)
        self.lbl_result_appele.setMinimumSize(size)
        self.lbl_result_appele.setAlignment(Qt.AlignCenter)
        self.lbl_point_defense.setAlignment(Qt.AlignCenter)
        self.lbl_result_defense.setFont(font)
        self.lbl_result_defense.setMinimumSize(size)
        self.lbl_result_defense.setAlignment(Qt.AlignCenter)
        self.btn_valider.setEnabled(False)
        self.lbl_pnj.setText(f"PNJ : {self.pnj}")

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)

        self.principal_layout = QHBoxLayout(self.gb_principal)
        self.preneur_layout = QVBoxLayout()
        self.contrat_layout = QVBoxLayout()
        self.bout_layout = QVBoxLayout()
        self.point_layout = QVBoxLayout()
        self.option_point_layout = QHBoxLayout()
        self.tete_layout = QVBoxLayout()
        self.appele_layout = QVBoxLayout()

        self.bonus_malus_layout = QHBoxLayout(self.gb_bonus_malus)
        self.poignee_layout = QVBoxLayout()
        self.petit_layout = QVBoxLayout()
        self.pt_chelem_layout = QVBoxLayout()
        self.gd_chelem_layout = QVBoxLayout()

        self.resultat_layout = QHBoxLayout()
        self.resultat_preneur_layout = QVBoxLayout()
        self.resultat_appele_layout = QVBoxLayout()
        self.resultat_defense_layout = QVBoxLayout()
        self.bouton_layout = QHBoxLayout()
        self.pnj_layout = QVBoxLayout()

    def add_widgets_to_layouts(self):
        self.preneur_layout.addWidget(self.lbl_preneur)
        self.preneur_layout.addWidget(self.cbx_preneur)
        self.contrat_layout.addWidget(self.lbl_contrat)
        self.contrat_layout.addWidget(self.cbx_contrat)
        self.bout_layout.addWidget(self.lbl_bout)
        self.bout_layout.addWidget(self.cbx_bout)
        self.point_layout.addWidget(self.lbl_point)
        self.option_point_layout.addWidget(self.le_point)
        self.option_point_layout.addWidget(self.btn_attaque_def)
        self.point_layout.addLayout(self.option_point_layout)
        self.tete_layout.addWidget(self.lbl_tete)
        self.tete_layout.addWidget(self.cbx_tete)
        self.appele_layout.addWidget(self.lbl_appele)
        self.appele_layout.addWidget(self.cbx_appele)

        self.principal_layout.addLayout(self.preneur_layout)
        self.principal_layout.addLayout(self.contrat_layout)
        self.principal_layout.addLayout(self.bout_layout)
        self.principal_layout.addLayout(self.point_layout)
        self.principal_layout.addLayout(self.tete_layout)
        self.principal_layout.addLayout(self.appele_layout)
        self.main_layout.addWidget(self.gb_principal)

        self.poignee_layout.addWidget(self.lbl_poignee)
        self.poignee_layout.addWidget(self.cbx_poignee)
        self.petit_layout.addWidget(self.lbl_petit)
        self.petit_layout.addWidget(self.cbx_petit)
        self.pt_chelem_layout.addWidget(self.lbl_pt_chelem)
        self.pt_chelem_layout.addWidget(self.cbx_pt_chelem)
        self.gd_chelem_layout.addWidget(self.lbl_gd_chelem)
        self.gd_chelem_layout.addWidget(self.cbx_gd_chelem)

        self.bonus_malus_layout.addLayout(self.poignee_layout)
        self.bonus_malus_layout.addLayout(self.petit_layout)
        self.bonus_malus_layout.addLayout(self.pt_chelem_layout)
        self.bonus_malus_layout.addLayout(self.gd_chelem_layout)
        self.main_layout.addWidget(self.gb_bonus_malus)

        self.main_layout.addSpacerItem(self.spacer_sep)

        self.resultat_layout.addSpacerItem(self.spacer_gauche)
        self.resultat_preneur_layout.addWidget(self.lbl_point_preneur)
        self.resultat_preneur_layout.addWidget(self.lbl_result_preneur)
        self.resultat_layout.addLayout(self.resultat_preneur_layout)
        if self.nb_joueurs > 4:
            self.resultat_appele_layout.addWidget(self.lbl_point_appele)
            self.resultat_appele_layout.addWidget(self.lbl_result_appele)
            self.resultat_layout.addLayout(self.resultat_appele_layout)
        self.resultat_defense_layout.addWidget(self.lbl_point_defense)
        self.resultat_defense_layout.addWidget(self.lbl_result_defense)
        self.resultat_layout.addLayout(self.resultat_defense_layout)
        self.resultat_layout.addWidget(self.lbl_result_preneur)
        self.resultat_layout.addSpacerItem(self.spacer_milieu)
        if self.pnj:
            self.bouton_layout.addWidget(self.btn_valider)
            self.bouton_layout.addWidget(self.btn_annuler)
            self.pnj_layout.addLayout(self.bouton_layout)
            self.pnj_layout.addWidget(self.lbl_pnj)
            self.resultat_layout.addLayout(self.pnj_layout)
        else:
            self.resultat_layout.addWidget(self.btn_valider)
            self.resultat_layout.addWidget(self.btn_annuler)
        self.resultat_layout.addSpacerItem(self.spacer_droite)
        self.main_layout.addLayout(self.resultat_layout)

    def setup_connections(self):
        self.btn_valider.clicked.connect(self.valider_donne)
        self.btn_annuler.clicked.connect(self.close)
        self.cbx_preneur.currentIndexChanged.connect(self.maj_preneur_appele)
        self.cbx_contrat.currentIndexChanged.connect(self.check_complete)
        self.cbx_bout.currentIndexChanged.connect(self.check_complete)
        self.le_point.textChanged.connect(self.check_complete)
        self.btn_attaque_def.clicked.connect(self.point_attaque_def)
        self.cbx_tete.currentIndexChanged.connect(self.check_complete)
        self.cbx_appele.currentIndexChanged.connect(self.maj_preneur_appele)
        self.cbx_poignee.currentIndexChanged.connect(self.check_complete)
        self.cbx_petit.currentIndexChanged.connect(self.check_complete)
        self.cbx_pt_chelem.currentIndexChanged.connect(self.check_complete)
        self.cbx_gd_chelem.currentIndexChanged.connect(self.check_complete)

    def affichage_modif(self):
        """Affiche les paramètres d'une donne en particulier lorsque
        la fenêtre est appelée en mode modification."""
        self.cbx_preneur.setCurrentText(self.modif[0])
        self.cbx_contrat.setCurrentText(self.modif[1])
        self.cbx_bout.setCurrentText(self.modif[2])
        self.le_point.setText(self.modif[3])
        if self.nb_joueurs > 4:
            self.cbx_tete.setCurrentText(self.modif[4])
            self.cbx_appele.setCurrentText(self.modif[5])
            self.cbx_petit.setCurrentText(self.modif[6])
            self.cbx_poignee.setCurrentText(self.modif[7])
            self.cbx_pt_chelem.setCurrentText(self.modif[8])
            self.cbx_gd_chelem.setCurrentText(self.modif[9])
        else:
            self.cbx_petit.setCurrentText(self.modif[4])
            self.cbx_poignee.setCurrentText(self.modif[5])
            self.cbx_pt_chelem.setCurrentText(self.modif[6])
            self.cbx_gd_chelem.setCurrentText(self.modif[7])

    def valider_donne(self):
        """Emet avant fermeture de la fenêtre les paramètres de la donne."""
        if self.pnj:
            param_donne = [self.pnj,
                           self.preneur,
                           self.contrat,
                           self.bout,
                           self.point,
                           self.tete,
                           self.appele,
                           self.poignee,
                           self.petit,
                           self.pt_che,
                           self.gd_che]
        elif self.nb_joueurs == 5:
            param_donne = [self.preneur,
                           self.contrat,
                           self.bout,
                           self.point,
                           self.tete,
                           self.appele,
                           self.poignee,
                           self.petit,
                           self.pt_che,
                           self.gd_che]
        else:
            param_donne = [self.preneur,
                           self.contrat,
                           self.bout,
                           self.point,
                           self.poignee,
                           self.petit,
                           self.pt_che,
                           self.gd_che]
        repartition = [self.lbl_result_preneur.text(),
                       self.lbl_result_appele.text(),
                       self.lbl_result_defense.text()]
        self.donne_valid.emit(param_donne, self.ligne_donne, repartition)
        self.close()

    def point_attaque_def(self):
        """Change, entre attaque et défense, la signication des points saisies."""
        is_attaque = self.btn_attaque_def.text() == "Att"
        self.point_de_lattaque = not is_attaque
        self.btn_attaque_def.setText("Def" if is_attaque else "Att")

        self.check_complete()

    def check_complete(self):
        """Appel la méthode d'activation du bouton valider si les champs
        obligatoires sont renseignés et les règles de validations respectées"""
        self.get_values_from_text_fields()

        if all([self.preneur, self.contrat, self.bout, self.point, self.tete, self.appele]):
            self.point = point_preneur_float(self.point, self.point_de_lattaque)
            if (
                    all([self.pt_che, self.gd_che])
                    or self.point < 69
                    and self.pt_che
                    or self.point < 86.5
                    and self.gd_che in ["Annoncé", "Non annoncé"]
            ):
                self.activation_btn_valider(False)
            else:
                self.activation_btn_valider(True)
        else:
            self.activation_btn_valider(False)

    def get_values_from_text_fields(self):
        self.preneur = self.cbx_preneur.currentText()
        self.contrat = self.cbx_contrat.currentText()
        self.bout = self.cbx_bout.currentText()
        self.point = self.le_point.text()
        self.tete = self.cbx_tete.currentText() if self.nb_joueurs > 4 else "none"
        self.appele = self.cbx_appele.currentText() if self.nb_joueurs > 4 else "none"
        self.poignee = self.cbx_poignee.currentText()
        self.petit = self.cbx_petit.currentText()
        self.pt_che = self.cbx_pt_chelem.currentText()
        self.gd_che = self.cbx_gd_chelem.currentText()

    def activation_btn_valider(self, actif):
        """Active ou pas le bouton valider et affiche
        la répartition des points entre attaque et défense."""
        if actif:
            self.btn_valider.setEnabled(True)

            resultat = self.calcul_resultat_donne()
            self.affichage_valeur_repartition(resultat)
            self.coloration_repartition(resultat)
        else:
            self.btn_valider.setEnabled(False)

            self.lbl_result_preneur.setText("")
            self.lbl_result_appele.setText("")
            self.lbl_result_defense.setText("")

    def calcul_resultat_donne(self):
        """Retourne les points de la donne en cours."""
        return calcul_donne(self.contrat, self.bout, self.point,
                            self.poignee, self.petit, self.pt_che, self.gd_che)

    def affichage_valeur_repartition(self, resultat):
        if self.appele in ["Chien", "Solo"]:
            coef = 4
            self.lbl_result_appele.setText("")
        elif self.nb_joueurs == 3 or self.nb_joueurs > 4:
            coef = 2
            self.lbl_result_appele.setText(str(resultat))
        else:
            coef = 3
            self.lbl_result_appele.setText(str(resultat))
        self.lbl_result_preneur.setText(str(resultat * coef))
        self.lbl_result_defense.setText(str(resultat * -1))

    def coloration_repartition(self, resultat):
        if resultat >= 0:
            self.lbl_result_preneur.setStyleSheet("color: green")
            self.lbl_result_appele.setStyleSheet("color: green")
            self.lbl_result_defense.setStyleSheet("color: red")
        else:
            self.lbl_result_preneur.setStyleSheet("color: red")
            self.lbl_result_appele.setStyleSheet("color: red")
            self.lbl_result_defense.setStyleSheet("color: green")

    def maj_preneur_appele(self):
        """Met à jour les combobox preneur et appele entre elles :
        sélection d'une valeur dans l'une implique le retrait de cette dernière dans l'autre."""
        if self.traitement:
            return

        preneur, appele = self.cbx_preneur.currentText(), self.cbx_appele.currentText()
        liste_preneur = [elem for elem in self.joueurs if elem != appele]
        liste_appele = [elem for elem in self.joueurs if elem != preneur]

        self.fill_cbx_preneur_appele(liste_preneur, liste_appele)

        self.traitement = True
        if preneur:
            self.cbx_preneur.setCurrentText(preneur)
        else:
            self.cbx_preneur.setCurrentIndex(-1)
        if appele:
            self.cbx_appele.setCurrentText(appele)
        else:
            self.cbx_appele.setCurrentIndex(-1)
        self.traitement = False

        self.check_complete()

    def fill_cbx_preneur_appele(self, list_p, list_a):
        """Affiche dans les comboxbox preneur et appele la liste des joueurs
        disponibles pour chacun."""
        self.traitement = True
        self.cbx_preneur.clear()
        self.cbx_preneur.addItems(list_p)
        if self.nb_joueurs > 4:
            self.cbx_appele.clear()
            self.cbx_appele.addItems(list_a)
            self.cbx_appele.addItems(["Chien", "Solo"])
        self.traitement = False


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    window = DetailsWindow(
        joueurs=["Romain", "Ludo", "Emeline", "Eddy", "Aurore"],
        ligne=0,
        modif=(),
        pnj=""
    )
    window.show()
    app.exec()
