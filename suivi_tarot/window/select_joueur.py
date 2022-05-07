from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QAbstractItemView

from suivi_tarot.database.clients import get_active_players
from suivi_tarot.window.table import TableWindow


# noinspection PyAttributeOutsideInit
class SelectPlayerWindow(QWidget):
    """Fenêtre de sélection des joueurs participants à la session"""
    def __init__(self):
        super().__init__()

        self.selected_players = set()
        self.selection_order = {}
        self.resize(176, 344)
        self.setWindowTitle("Sélection des joueurs")
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_liste = QLabel("Joueurs autour de la table :")
        self.lw_player = QListWidget()
        self.lbl_number_players = QLabel("0 sélectionné")
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.btn_validate.setEnabled(False)
        self.lw_player.addItems(get_active_players())
        self.lw_player.setSelectionMode(QAbstractItemView.MultiSelection)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_liste)
        self.main_layout.addWidget(self.lw_player)
        self.main_layout.addWidget(self.lbl_number_players)
        self.button_layout.addWidget(self.btn_validate)
        self.button_layout.addWidget(self.btn_cancel)
        self.main_layout.addLayout(self.button_layout)

    def setup_connections(self):
        self.lw_player.itemSelectionChanged.connect(self.select_player)
        self.btn_validate.clicked.connect(self.launch_game)
        self.btn_cancel.clicked.connect(self.close)

    def select_player(self):
        """Lance les actions après un changement de sélection dans le ListWidget"""
        self.order_of_selection()
        self.update_interface()

    def update_interface(self):
        """Active ou non le bouton valider en fonction du nombre de joueurs sélectionnés
        et affichage de ce dernier"""
        number_select = len(self.selected_players)

        self.btn_validate.setEnabled(2 < number_select < 7)
        self.lbl_number_players.setText(f"{number_select} sélectionné{'s' if number_select > 1 else ''}")

    def order_of_selection(self):
        """Sauvegarde de l'ordre dans lequel les pseudos sont sélectionnés"""
        new_selected_players = {elem.text() for elem in self.lw_player.selectedItems()}
        if new_selected_players - self.selected_players:
            nickname = (new_selected_players - self.selected_players).pop()
            self.selected_players.add(nickname)
            self.selection_order[nickname] = len(self.selected_players)
        else:
            nickname = (self.selected_players - new_selected_players).pop()
            self.selected_players.remove(nickname)
            rang = self.selection_order[nickname]
            del self.selection_order[nickname]
            for cle in self.selection_order:
                if self.selection_order[cle] > rang:
                    self.selection_order[cle] -= 1

    def launch_game(self):
        """Ouvre la fenêtre d'enregistrement d'une session"""
        player_table = self.create_list_player_sorted()

        self.table = TableWindow(player_table)
        self.table.setWindowModality(Qt.ApplicationModal)
        self.close()
        self.table.show()

    def create_list_player_sorted(self):
        """Création de la liste des pseudos dans l'ordre où ils ont été sélectionnés"""
        list_sorted = []
        i = 1
        while self.selection_order:
            for nickname, rang in self.selection_order.items():
                if self.selection_order[nickname] == i:
                    list_sorted.append(nickname)
                    del self.selection_order[nickname]
                    break
            i += 1

        return list_sorted


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication


    app = QApplication()
    window = SelectPlayerWindow()
    window.show()
    app.exec()
