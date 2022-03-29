"""Point d'entrée du programme. Actions :
- Lance la création d'une bdd s'il elle n'est pas trouvé
- Affiche la fenêtre principale du programme"""

import sys

from PySide6.QtWidgets import QApplication

from window.main_window import MainWindow
from api.utils import DATA_FILE
from database.clients import init_bdd


if __name__ == '__main__':
    if not DATA_FILE.exists():
        init_bdd()

    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
