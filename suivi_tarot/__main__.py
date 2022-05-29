"""Point d'entrée du programme. Actions :
- Lance la création d'une bdd s'il elle n'est pas trouvé
- Affiche la fenêtre principale du programme"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from suivi_tarot.window.db_connection import BddWindow
from suivi_tarot.api.utils import CONFIG_FILE
from suivi_tarot.database.manage import create_config_file, get_path_database


def init_app(application: QApplication, message: str, path_default: Path = ""):
    """Lance la fenêtre de connexion de l'application à une base de données"""
    win = BddWindow(message, str(path_default))
    win.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    app = QApplication()
    if not CONFIG_FILE.exists():
        create_config_file()
        init_app(app, "new")

    path, valid = get_path_database(".sqlite3")
    if not valid:
        init_app(app, "error", path)

    from suivi_tarot.window.main_window import MainWindow

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
