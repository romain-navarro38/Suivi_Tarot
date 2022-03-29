from PySide6.QtGui import QRegularExpressionValidator, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QLineEdit, QComboBox, \
    QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt, QSize, Signal

from api.utils import TETE
from api.calcul import calcul_donne, point_preneur_float, Contract, Poignee, \
    calculation_distribution_point_between_player, conversion_contract, conversion_poignee


# noinspection PyAttributeOutsideInit
class DetailsWindow(QWidget):
    """Fenêtre permettant la création ou la modification d'une donne
    pour la session en cours"""

    donne_valid = Signal(list, int, list)

    def __init__(self, players: list[str], ligne: int, modif: tuple, pnj: str):
        super().__init__()

        self.players = players
        self.number_players = len(players)
        self.ligne_donne = ligne
        self.pnj = pnj
        self.modif = list(modif)
        self.point_of_attack = True
        self.setup_ui()
        self.resize(505, 192)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        if self.modif:
            self.displaying_editing()

    def create_widgets(self):
        self.gb_principal = QGroupBox(self)
        self.lbl_preneur = QLabel(self.gb_principal)
        self.cbx_preneur = QComboBox(self.gb_principal)
        self.lbl_contract = QLabel(self.gb_principal)
        self.cbx_contract = QComboBox(self.gb_principal)
        self.lbl_bout = QLabel(self.gb_principal)
        self.cbx_bout = QComboBox(self.gb_principal)
        self.lbl_point = QLabel(self.gb_principal)
        self.le_point = QLineEdit(self.gb_principal)
        self.btn_attack_defense = QPushButton(self.gb_principal)
        self.lbl_tete = QLabel(self.gb_principal)
        self.cbx_tete = QComboBox(self.gb_principal)
        self.lbl_appele = QLabel(self.gb_principal)
        self.cbx_appele = QComboBox(self.gb_principal)

        self.gb_bonus_malus = QGroupBox(self)
        self.lbl_poignee = QLabel(self.gb_bonus_malus)
        self.cbx_poignee = QComboBox(self.gb_bonus_malus)
        self.lbl_petit = QLabel(self.gb_bonus_malus)
        self.cbx_petit = QComboBox(self.gb_bonus_malus)
        self.lbl_petit_chelem = QLabel(self.gb_bonus_malus)
        self.cbx_petit_chelem = QComboBox(self.gb_bonus_malus)
        self.lbl_grand_chelem = QLabel(self.gb_bonus_malus)
        self.cbx_grand_chelem = QComboBox(self.gb_bonus_malus)

        self.spacer_sep = QSpacerItem(378, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.spacer_left = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.lbl_point_preneur = QLabel("Preneur")
        self.lbl_result_preneur = QLabel("")
        self.lbl_point_appele = QLabel("Appelé")
        self.lbl_result_appele = QLabel("")
        self.lbl_point_defense = QLabel("Défense")
        self.lbl_result_defense = QLabel("")
        self.spacer_middle = QSpacerItem(1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")
        self.spacer_right = QSpacerItem(2, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.lbl_pnj = QLabel("")

    def modify_widgets(self):
        self.lbl_preneur.setAlignment(Qt.AlignCenter)
        self.lbl_preneur.setText("Preneur")
        self.fill_combobox_preneur_appele(self.players, self.players)
        self.cbx_preneur.setCurrentIndex(-1)
        self.lbl_contract.setAlignment(Qt.AlignCenter)
        self.lbl_contract.setText("Contrat")
        self.cbx_contract.addItems([contrat.name for contrat in Contract])
        self.cbx_contract.setCurrentIndex(-1)
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
        self.btn_attack_defense.setMaximumSize(QSize(40, 16777215))
        self.btn_attack_defense.setText("Att")
        if self.number_players > 4:
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
        self.cbx_poignee.addItems([""])
        self.cbx_poignee.addItems([poignee.name for poignee in Poignee])
        self.cbx_poignee.setCurrentIndex(-1)
        self.lbl_petit.setAlignment(Qt.AlignCenter)
        self.lbl_petit.setText("Petit au bout")
        self.cbx_petit.addItems(["", "Gagné", "Perdu"])
        self.cbx_petit.setCurrentIndex(-1)
        self.lbl_petit_chelem.setAlignment(Qt.AlignCenter)
        self.lbl_petit_chelem.setText("Petit chelem")
        self.cbx_petit_chelem.addItems(["", "Oui"])
        self.cbx_petit_chelem.setCurrentIndex(-1)
        self.lbl_grand_chelem.setAlignment(Qt.AlignCenter)
        self.lbl_grand_chelem.setText("Grand chelem")
        self.cbx_grand_chelem.addItems(["", "Réussi", "Réussi ss annonce", "Raté"])
        self.cbx_grand_chelem.setCurrentIndex(-1)
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
        self.btn_validate.setEnabled(False)
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

        self.result_layout = QHBoxLayout()
        self.result_preneur_layout = QVBoxLayout()
        self.result_appele_layout = QVBoxLayout()
        self.result_defense_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.pnj_layout = QVBoxLayout()

    def add_widgets_to_layouts(self):
        self.preneur_layout.addWidget(self.lbl_preneur)
        self.preneur_layout.addWidget(self.cbx_preneur)
        self.contrat_layout.addWidget(self.lbl_contract)
        self.contrat_layout.addWidget(self.cbx_contract)
        self.bout_layout.addWidget(self.lbl_bout)
        self.bout_layout.addWidget(self.cbx_bout)
        self.point_layout.addWidget(self.lbl_point)
        self.option_point_layout.addWidget(self.le_point)
        self.option_point_layout.addWidget(self.btn_attack_defense)
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
        self.pt_chelem_layout.addWidget(self.lbl_petit_chelem)
        self.pt_chelem_layout.addWidget(self.cbx_petit_chelem)
        self.gd_chelem_layout.addWidget(self.lbl_grand_chelem)
        self.gd_chelem_layout.addWidget(self.cbx_grand_chelem)

        self.bonus_malus_layout.addLayout(self.poignee_layout)
        self.bonus_malus_layout.addLayout(self.petit_layout)
        self.bonus_malus_layout.addLayout(self.pt_chelem_layout)
        self.bonus_malus_layout.addLayout(self.gd_chelem_layout)
        self.main_layout.addWidget(self.gb_bonus_malus)

        self.main_layout.addSpacerItem(self.spacer_sep)

        self.result_layout.addSpacerItem(self.spacer_left)
        self.result_preneur_layout.addWidget(self.lbl_point_preneur)
        self.result_preneur_layout.addWidget(self.lbl_result_preneur)
        self.result_layout.addLayout(self.result_preneur_layout)
        if self.number_players > 4:
            self.result_appele_layout.addWidget(self.lbl_point_appele)
            self.result_appele_layout.addWidget(self.lbl_result_appele)
            self.result_layout.addLayout(self.result_appele_layout)
        self.result_defense_layout.addWidget(self.lbl_point_defense)
        self.result_defense_layout.addWidget(self.lbl_result_defense)
        self.result_layout.addLayout(self.result_defense_layout)
        self.result_layout.addWidget(self.lbl_result_preneur)
        self.result_layout.addSpacerItem(self.spacer_middle)
        if self.pnj:
            self.button_layout.addWidget(self.btn_validate)
            self.button_layout.addWidget(self.btn_cancel)
            self.pnj_layout.addLayout(self.button_layout)
            self.pnj_layout.addWidget(self.lbl_pnj)
            self.result_layout.addLayout(self.pnj_layout)
        else:
            self.result_layout.addWidget(self.btn_validate)
            self.result_layout.addWidget(self.btn_cancel)
        self.result_layout.addSpacerItem(self.spacer_right)
        self.main_layout.addLayout(self.result_layout)

    def setup_connections(self):
        self.btn_validate.clicked.connect(self.validate_donne)
        self.btn_cancel.clicked.connect(self.close)
        self.cbx_preneur.currentIndexChanged.connect(self.update_preneur_appele)
        self.cbx_contract.currentIndexChanged.connect(self.check_complete)
        self.cbx_bout.currentIndexChanged.connect(self.check_complete)
        self.le_point.textChanged.connect(self.check_complete)
        self.btn_attack_defense.clicked.connect(self.point_attack_defense)
        self.cbx_tete.currentIndexChanged.connect(self.check_complete)
        self.cbx_appele.currentIndexChanged.connect(self.update_preneur_appele)
        self.cbx_poignee.currentIndexChanged.connect(self.check_complete)
        self.cbx_petit.currentIndexChanged.connect(self.check_complete)
        self.cbx_petit_chelem.currentIndexChanged.connect(self.check_complete)
        self.cbx_grand_chelem.currentIndexChanged.connect(self.check_complete)

    def displaying_editing(self):
        """Affiche les paramètres d'une donne en particulier lorsque
        la fenêtre est appelée en mode modification."""
        self.cbx_preneur.setCurrentText(self.modif[0])
        self.cbx_contract.setCurrentText(self.modif[1])
        self.cbx_bout.setCurrentText(self.modif[2])
        self.le_point.setText(self.modif[3])
        if self.number_players > 4:
            self.cbx_tete.setCurrentText(self.modif[4])
            self.cbx_appele.setCurrentText(self.modif[5])
            self.cbx_petit.setCurrentText(self.modif[6])
            self.cbx_poignee.setCurrentText(self.modif[7])
            self.cbx_petit_chelem.setCurrentText(self.modif[8])
            self.cbx_grand_chelem.setCurrentText(self.modif[9])
        else:
            self.cbx_petit.setCurrentText(self.modif[4])
            self.cbx_poignee.setCurrentText(self.modif[5])
            self.cbx_petit_chelem.setCurrentText(self.modif[6])
            self.cbx_grand_chelem.setCurrentText(self.modif[7])

    def validate_donne(self):
        """Emet avant fermeture de la fenêtre les paramètres de la donne."""
        if self.pnj:
            param_donne = [self.pnj,
                           self.preneur,
                           self.cbx_contract.currentText(),
                           self.bout,
                           self.point,
                           self.tete,
                           self.appele,
                           self.cbx_poignee.currentText(),
                           self.petit,
                           self.petit_chelem,
                           self.grand_chelem]
        elif self.number_players == 5:
            param_donne = [self.preneur,
                           self.cbx_contract.currentText(),
                           self.bout,
                           self.point,
                           self.tete,
                           self.appele,
                           self.cbx_poignee.currentText(),
                           self.petit,
                           self.petit_chelem,
                           self.grand_chelem]
        else:
            param_donne = [self.preneur,
                           self.cbx_contract.currentText(),
                           self.bout,
                           self.point,
                           self.cbx_poignee.currentText(),
                           self.petit,
                           self.petit_chelem,
                           self.grand_chelem]
        repartition = [self.lbl_result_preneur.text(),
                       self.lbl_result_appele.text(),
                       self.lbl_result_defense.text()]
        self.donne_valid.emit(param_donne, self.ligne_donne, repartition)
        self.close()

    def point_attack_defense(self):
        """Change, entre attaque et défense, la signication des points saisies."""
        is_attaque = self.btn_attack_defense.text() == "Att"
        self.point_of_attack = not is_attaque
        self.btn_attack_defense.setText("Def" if is_attaque else "Att")

        self.check_complete()

    def check_complete(self):
        """Appel la méthode d'activation du bouton valider si les champs
        obligatoires sont renseignés et les règles de validations respectées"""
        self.get_values_from_text_fields()

        if all([self.preneur, self.contract, self.bout, self.point, self.tete, self.appele]):
            self.point = point_preneur_float(self.point, self.point_of_attack)
            if (
                    all([self.petit_chelem, self.grand_chelem])
                    or self.point < 69
                    and self.petit_chelem
                    or self.point < 86.5
                    and self.grand_chelem in ["Annoncé", "Non annoncé"]
            ):
                self.activation_button_validate(False)
            else:
                self.activation_button_validate(True)
        else:
            self.activation_button_validate(False)

    def get_values_from_text_fields(self):
        self.preneur = self.cbx_preneur.currentText()
        self.contract = conversion_contract(self.cbx_contract.currentText())
        self.bout = self.cbx_bout.currentText()
        self.point = self.le_point.text()
        self.tete = self.cbx_tete.currentText() if self.number_players > 4 else "none"
        self.appele = self.cbx_appele.currentText() if self.number_players > 4 else "none"
        self.poignee = conversion_poignee(self.cbx_poignee.currentText())
        self.petit = self.cbx_petit.currentText()
        self.petit_chelem = self.cbx_petit_chelem.currentText()
        self.grand_chelem = self.cbx_grand_chelem.currentText()

    def activation_button_validate(self, actif: bool):
        """Active ou pas le bouton valider et affiche
        la répartition des points entre attaque et défense."""
        self.btn_validate.setEnabled(actif)
        if actif:
            resultat = self.calculation_result_donne()
            self.displaying_distribution_value(resultat)
            self.coloring_distribution(resultat)
        else:
            self.lbl_result_preneur.setText("")
            self.lbl_result_appele.setText("")
            self.lbl_result_defense.setText("")

    def calculation_result_donne(self) -> int:
        """Retourne les points de la donne en cours."""
        return calcul_donne(self.contract, self.bout, self.point,
                            self.poignee, self.petit, self.petit_chelem, self.grand_chelem)

    def displaying_distribution_value(self, result: int):
        preneur, appele, defense = calculation_distribution_point_between_player(result, self.appele,
                                                                                 self.number_players)

        self.lbl_result_preneur.setText(str(preneur))
        self.lbl_result_appele.setText(str(appele))
        self.lbl_result_defense.setText(str(defense))

    def coloring_distribution(self, resultat: int):
        if resultat >= 0:
            self.lbl_result_preneur.setStyleSheet("color: green")
            self.lbl_result_appele.setStyleSheet("color: green")
            self.lbl_result_defense.setStyleSheet("color: red")
        else:
            self.lbl_result_preneur.setStyleSheet("color: red")
            self.lbl_result_appele.setStyleSheet("color: red")
            self.lbl_result_defense.setStyleSheet("color: green")

    def update_preneur_appele(self):
        """Met à jour les combobox preneur et appele entre elles :
        sélection d'une valeur dans l'une implique le retrait de cette dernière dans l'autre."""
        if self.treatment:
            return

        preneur, appele = self.cbx_preneur.currentText(), self.cbx_appele.currentText()
        liste_preneur = [elem for elem in self.players if elem != appele]
        liste_appele = [elem for elem in self.players if elem != preneur]

        self.fill_combobox_preneur_appele(liste_preneur, liste_appele)

        self.treatment = True
        if preneur:
            self.cbx_preneur.setCurrentText(preneur)
        else:
            self.cbx_preneur.setCurrentIndex(-1)
        if appele:
            self.cbx_appele.setCurrentText(appele)
        else:
            self.cbx_appele.setCurrentIndex(-1)
        self.treatment = False

        self.check_complete()

    def fill_combobox_preneur_appele(self, list_preneur: list[str], list_appele: list[str]):
        """Affiche dans les comboxbox preneur et appele la liste des joueurs
        disponibles pour chacun."""
        self.treatment = True
        self.cbx_preneur.clear()
        self.cbx_preneur.addItems(list_preneur)
        if self.number_players > 4:
            self.cbx_appele.clear()
            self.cbx_appele.addItems(list_appele)
            self.cbx_appele.addItems(["Chien", "Solo"])
        self.treatment = False


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from api.utils import PLAYERS

    app = QApplication()
    window = DetailsWindow(players=PLAYERS, ligne=0, modif=(), pnj="")
    window.show()
    app.exec()
