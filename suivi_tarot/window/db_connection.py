from PySide6.QtWidgets import QApplication, QWidget, QRadioButton, QLineEdit, QPushButton, QHBoxLayout, \
    QVBoxLayout, QFormLayout, QFileDialog, QMessageBox

from suivi_tarot.api.check import path_is_existing_folder_or_file, check_length_str, Comparison
from suivi_tarot.database.clients import init_bdd
from suivi_tarot.api.settings import add_path_database


# noinspection PyAttributeOutsideInit
class BddWindow(QWidget):
    """Fenêtre de connexion de l'application à une base de données.
    S'affiche à la première utilisation de l'application ou lorsque
    ou lorsque le chemin à la bdd est invalide."""
    def __init__(self, type_message: str, path_default: str = ""):
        super().__init__()

        self.type_message = type_message
        self.path_default = path_default
        self.setup_ui()
        self.change_ui()
        self.le_path.setText(self.path_default)
        self.message()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.rdb_new_database = QRadioButton("Nouvelle base de données")
        self.rdb_existing_database = QRadioButton("Base de données existante")
        self.le_path = QLineEdit()
        self.btn_search_path = QPushButton("")
        self.le_password = QLineEdit()
        self.le_confirm = QLineEdit()
        self.btn_validate = QPushButton("")
        self.btn_close = QPushButton("Fermer")

    def modify_widgets(self):
        if self.type_message == "new":
            self.rdb_new_database.setChecked(True)
        else:
            self.rdb_existing_database.setChecked(True)
        self.le_password.setEchoMode(QLineEdit.Password)
        self.le_password.setPlaceholderText("6 caractères minimum")
        self.le_confirm.setEchoMode(QLineEdit.Password)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.choice_layout = QHBoxLayout()
        self.path_layout = QVBoxLayout()
        self.password_layout = QFormLayout()
        self.btn_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.choice_layout.addWidget(self.rdb_new_database)
        self.choice_layout.addWidget(self.rdb_existing_database)
        self.path_layout.addWidget(self.le_path)
        self.path_layout.addWidget(self.btn_search_path)
        self.password_layout.addRow("Mot de passe", self.le_password)
        self.password_layout.addRow("Confirmation", self.le_confirm)
        self.btn_layout.addWidget(self.btn_validate)
        self.btn_layout.addWidget(self.btn_close)
        self.main_layout.addLayout(self.choice_layout)
        self.main_layout.addLayout(self.path_layout)
        self.main_layout.addLayout(self.password_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.rdb_new_database.clicked.connect(self.change_ui)
        self.rdb_existing_database.clicked.connect(self.change_ui)
        self.btn_search_path.clicked.connect(self.search)
        self.btn_validate.clicked.connect(self.validate)
        self.btn_close.clicked.connect(self.close)

    def change_ui(self):
        """Modifie l'ui en fonction du radiobutton sélectionné"""
        if self.rdb_new_database.isChecked():
            self.le_path.clear()
            self.btn_search_path.setText("Sélectionner le dossier de destination")
            self.le_password.setEnabled(True)
            self.le_confirm.setEnabled(True)
            self.btn_validate.setText("Créer")
        else:
            self.le_path.clear()
            self.btn_search_path.setText("Rechercher une base de données")
            self.le_password.clear()
            self.le_password.setEnabled(False)
            self.le_confirm.clear()
            self.le_confirm.setEnabled(False)
            self.btn_validate.setText("Associer")

    def message(self):
        """Message explicatif s'affichant avant la fenêtre"""
        msg = QMessageBox()
        if self.type_message == "new":
            msg.setIcon(QMessageBox.Information)
            msg.setText("Bienvenue, veuillez créer une nouvelle base de données ou en associer une déjà existante.")
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText("""Il y a une erreur avec le chemin de la base de données.
Veuillez rectifier ou créer une nouvelle base de données.""")

        msg.setInformativeText("L'application doit ensuite être relancée.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def search(self):
        """Ouvre une boite dialogue pour définir un chemin vers une bdd"""
        if self.rdb_new_database.isChecked():
            self.le_path.setText(QFileDialog.getExistingDirectory(self, "Sélectionner un dossier"))
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Rechercher un fichier",
                                                  filter="sqlite3 (*.sqlite3)")
            self.le_path.setText(path)

    def validate(self):
        """Vérification des informations saisies"""
        path = self.le_path.text()
        if self.rdb_new_database.isChecked():
            check_path = path_is_existing_folder_or_file(path, "folder")
            password_length = check_length_str(self.le_password.text(), 6,
                                               Comparison.GREATER_THAN_OR_EQUAL)
            confirm_password = self.le_password.text() == self.le_confirm.text()
        else:
            check_path = all([path_is_existing_folder_or_file(path, "file"),
                              path.endswith(".sqlite3")])
            password_length, confirm_password = True, True

        if all([check_path, password_length, confirm_password]):
            self.associate_database()
            self.close()

    def associate_database(self):
        """Enregistre le chemin de la bdd dans config.json et initialise
        l'initialise si c'est une création."""
        if self.rdb_new_database.isChecked():
            add_path_database(f'{self.le_path.text()}/db.sqlite3')
            init_bdd(self.le_path.text(), self.le_password.text())
        else:
            add_path_database(self.le_path.text())


if __name__ == '__main__':
    app = QApplication()
    window = BddWindow("new", "")
    window.show()
    app.exec()
