from functools import partial

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QCloseEvent
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QListWidget, QPushButton, QListWidgetItem, \
    QAbstractItemView, QInputDialog, QLineEdit

from suivi_tarot.api.verification import check_password
from suivi_tarot.database.clients import get_active_players, get_inactive_players, update_status_joueurs
from suivi_tarot.window.ajout_joueur import AddPlayerWindow
from suivi_tarot.api.utils import IMAGE_FOLDER


# noinspection PyAttributeOutsideInit
class ManagementPlayerWindow(QWidget):
    """Fenêtre permettant l'ajout de nouveau joueur et leur passage de la
    catégorie actif à inactif et vice-versa"""
    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.parent.setVisible(False)
        self.modif = {}
        self.new_player = False
        self.setup_ui()
        self.resize(318, 266)
        self.setWindowTitle("Gestion des joueurs")

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_inactive = QLabel("Inactif")
        self.lbl_active = QLabel("Actif")
        self.lw_inactive = QListWidget()
        self.lw_active = QListWidget()
        self.btn_transfert = QPushButton()
        self.btn_append = QPushButton("Ajouter")
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.lbl_inactive.setAlignment(Qt.AlignCenter)
        self.lbl_active.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.lbl_active.setFont(font)
        self.lbl_inactive.setFont(font)

        self.btn_transfert.setIcon(QIcon(str(IMAGE_FOLDER / "double_fleche_couleur.png")))
        self.btn_transfert.setIconSize(QSize(60, 40))
        self.btn_transfert.setFlat(True)

        self.lw_inactive.addItems(get_inactive_players())
        self.lw_inactive.setSelectionMode(QAbstractItemView.MultiSelection)
        self.lw_active.addItems(get_active_players())
        self.lw_active.setSelectionMode(QAbstractItemView.MultiSelection)

    def create_layouts(self):
        self.main_layout = QGridLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_inactive, 0, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_active, 0, 4, 1, 2)
        self.main_layout.addWidget(self.lw_inactive, 1, 0, 4, 2)
        self.main_layout.addWidget(self.lw_active, 1, 4, 4, 2)
        self.main_layout.addWidget(self.btn_transfert, 2, 2, 2, 2)
        self.main_layout.addWidget(self.btn_append, 0, 2, 1, 2)
        self.main_layout.addWidget(self.btn_validate, 5, 1, 1, 2)
        self.main_layout.addWidget(self.btn_cancel, 5, 3, 1, 2)

    def setup_connections(self):
        self.lw_inactive.itemDoubleClicked.connect(partial(self.unique_transfer, "inactive"))
        self.lw_active.itemDoubleClicked.connect(partial(self.unique_transfer, "active"))
        self.btn_append.clicked.connect(self.add_player)
        self.btn_transfert.clicked.connect(self.global_transfer)
        self.btn_validate.clicked.connect(self.save_change)
        self.btn_cancel.clicked.connect(self.close)

    def add_player(self):
        """Ouvre la fenêtre de création de nouveaux joueurs après vérification du mot de passe"""
        password, ok = QInputDialog.getText(self, "Papier svp !", "Mot de passe administrateur :", QLineEdit.Password)
        if ok and check_password(password):
            self.new_player = AddPlayerWindow()
            self.new_player.new_nickname.connect(self.add_nickname_to_lw)
            self.new_player.window_status.connect(self.update_window_status)
            self.new_player.show()

    def add_nickname_to_lw(self, player):
        """Ajoute un joueur à une des listes actif ou inactif après sa création."""
        if player["active"]:
            self.lw_active.addItem(player["nickname"])
        else:
            self.lw_inactive.addItem(player["nickname"])

    def update_window_status(self, status):
        """Renseigne l'état de la fenêtre de création de joueur permet de
        savoir s'il faut fermer cette dernière lorsque la fenêtre est fermée."""
        self.new_player = status

    def closeEvent(self, event: QCloseEvent) -> None:
        """À la fermeture de la fenêtre, ferme également celle
        de création de joueur si elle est ouverte"""
        if self.new_player:
            self.new_player.close()
        self.parent.setVisible(True)
        super().closeEvent(event)

    def unique_transfer(self, lw: str, item: QListWidgetItem):
        """Bascule l'item double-cliqué d'une liste à l'autre"""
        if lw == "inactive":
            lw_start = self.lw_inactive
            lw_end = self.lw_active
            status = True
        else:
            lw_start = self.lw_active
            lw_end = self.lw_inactive
            status = False

        row = lw_start.row(item)
        self.modif[item.text()] = status
        lw_end.addItem(lw_start.takeItem(row))

    def global_transfer(self):
        """Bascule tous les items sélectionnés entre les deux listes"""
        for item in self.lw_inactive.selectedItems():
            row = self.lw_inactive.row(item)
            self.modif[item.text()] = True
            self.lw_active.addItem(self.lw_inactive.takeItem(row))
        for item in self.lw_active.selectedItems():
            row = self.lw_active.row(item)
            self.modif[item.text()] = False
            self.lw_inactive.addItem(self.lw_active.takeItem(row))

    def save_change(self):
        """Sauvegarde en bdd l'attribut actif de chaque joueur"""
        if self.modif:
            update_status_joueurs(self.modif)
        self.close()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    window = ManagementPlayerWindow()
    window.show()
    app.exec()
