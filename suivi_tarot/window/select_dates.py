from datetime import datetime, timedelta

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QRadioButton, QComboBox, QHBoxLayout, \
    QLabel, QGridLayout, QDateTimeEdit, QPushButton

from suivi_tarot.database.clients import get_distinct_years, get_min_max_dates_parties


period_dict = {"type": ["Mois", "Trimestre", "Semestre"],
               "month": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
                         "octobre",
                         "novembre", "décembre"],
               "quarter": ["janvier - mars", "avril - juin", "juillet - septembre", "octobre - décembre"],
               "semester": ["janvier - juin", "juillet - décembre"],
               "janvier": [1, 1],
               "février": [2, 2],
               "mars": [3, 3],
               "avril": [4, 4],
               "mai": [5, 5],
               "juin": [6, 6],
               "juillet": [7, 7],
               "août": [8, 8],
               "septembre": [9, 9],
               "octobre": [10, 10],
               "novembre": [11, 11],
               "décembre": [12, 12],
               "janvier - mars": [1, 3],
               "avril - juin": [4, 6],
               "juillet - septembre": [7, 9],
               "octobre - décembre": [10, 12],
               "janvier - juin": [1, 6],
               "juillet - décembre": [7, 12]}


def font_bold() -> QFont:
    """Retourne une police en gras"""
    font = QFont()
    font.setBold(True)
    return font


def get_first_and_last_day_of_period(period: str, year: int) -> tuple[datetime, datetime]:
    """Retourne au format datetime le premier et le dernier jour d'une période"""
    start, end = period_dict.get(period)
    start = datetime(year, start, 1)
    end = datetime(year, end, 28, 23, 59, 59)
    next_month = end + timedelta(days=4)
    end = next_month - timedelta(days=next_month.day)
    return start, end


class CustomLabel(QLabel):
    """Création de label avec une police en gras et une longueur
    maximale de 40"""
    def __init__(self, text):
        super().__init__(text)

        self.setMaximumSize(QSize(40, 16777215))
        self.setFont(font_bold())


class CustomRadio(QRadioButton):
    """Création de radio bouton avec la police en gras"""
    def __init__(self, text):
        super().__init__(text)

        self.setFont(font_bold())


# noinspection PyAttributeOutsideInit
class SelectDates(QWidget):
    """Fenêtre servant à la sélection d'une période. Emet sous forme de datetime
    le premier et le dernier jour de cette période."""
    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.resize(269, 176)
        self.setWindowTitle("Recherche parties")

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_table_of = QLabel("Table de")
        self.cbx_table_of = QComboBox()
        self.lbl_players = QLabel("joueurs")

        self.tab_select_date = QTabWidget()

        self.widget_year = QWidget()
        self.radio_year = CustomRadio("Année")
        self.cbx_year = QComboBox()
        self.radio_rolling_year = CustomRadio("Derniers 12 mois")

        self.widget_period = QWidget()
        self.lbl_type_period = CustomLabel("Type")
        self.lbl_choice_period = CustomLabel("Choix")
        self.lbl_year_period = CustomLabel("Année")
        self.cbx_type_period = QComboBox()
        self.cbx_choice_period = QComboBox()
        self.cbx_year_period = QComboBox()

        self.widget_free = QWidget()
        self.lbl_from = CustomLabel("Du")
        self.lbl_to = CustomLabel("Au")
        self.dte_from = QDateTimeEdit()
        self.dte_to = QDateTimeEdit()

        self.btn_search = QPushButton("Rechercher")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.lbl_table_of.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.cbx_table_of.addItems(['3', '4', '5'])
        self.cbx_table_of.setCurrentIndex(2)
        self.cbx_table_of.setMaximumSize(QSize(30, 16777215))

        self.tab_select_date.setDocumentMode(True)
        self.tab_select_date.addTab(self.widget_year, "Année")
        self.widget_year.setAccessibleName("Année")
        self.tab_select_date.addTab(self.widget_period, "Période")
        self.widget_period.setAccessibleName("Période")
        self.tab_select_date.addTab(self.widget_free, "Libre")
        self.widget_free.setAccessibleName("Libre")

        self.radio_year.setChecked(True)
        self.radio_year.setMaximumSize(QSize(60, 16777215))
        self.available_years = get_distinct_years()
        if not self.available_years:
            self.available_years = [str(datetime.now().year)]
        self.cbx_year.addItems(self.available_years)

        self.cbx_type_period.addItems(period_dict["type"])
        self.cbx_year_period.addItems(self.available_years)
        self.update_cbx_choice_period()

        self.dte_from.setCalendarPopup(True)
        self.dte_to.setCalendarPopup(True)

        min_date, max_date = get_min_max_dates_parties()
        if min_date:
            min_date = min_date.replace(hour=0, minute=0, second=0)
            max_date = max_date.replace(hour=23, minute=59, second=59)
            self.dte_from.setDateTime(min_date)
            self.dte_to.setDateTime(max_date)
        else:
            year = datetime.now().year
            self.dte_from.setDateTime(datetime(year, 1, 1, 0, 0, 0))
            self.dte_to.setDateTime(datetime(year, 12, 31, 23, 59, 59))

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 9, 0, 9)

        self.table_players_layout = QHBoxLayout()

        self.year_layout = QVBoxLayout(self.widget_year)
        self.year_radio_cbx_layout = QHBoxLayout()
        self.period_layout = QGridLayout(self.widget_period)
        self.free_layout = QGridLayout(self.widget_free)

        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(9, 0, 9, 0)

    def add_widgets_to_layouts(self):
        self.table_players_layout.addWidget(self.lbl_table_of)
        self.table_players_layout.addWidget(self.cbx_table_of)
        self.table_players_layout.addWidget(self.lbl_players)

        self.year_radio_cbx_layout.addWidget(self.radio_year)
        self.year_radio_cbx_layout.addWidget(self.cbx_year)
        self.year_layout.addLayout(self.year_radio_cbx_layout)
        self.year_layout.addWidget(self.radio_rolling_year)

        self.period_layout.addWidget(self.lbl_type_period, 0, 0, 1, 1)
        self.period_layout.addWidget(self.cbx_type_period, 0, 1, 1, 1)
        self.period_layout.addWidget(self.lbl_choice_period, 1, 0, 1, 1)
        self.period_layout.addWidget(self.cbx_choice_period, 1, 1, 1, 1)
        self.period_layout.addWidget(self.lbl_year_period, 2, 0, 1, 1)
        self.period_layout.addWidget(self.cbx_year_period, 2, 1, 1, 1)

        self.free_layout.addWidget(self.lbl_from, 0, 0, 1, 1)
        self.free_layout.addWidget(self.dte_from, 0, 1, 1, 1)
        self.free_layout.addWidget(self.lbl_to, 1, 0, 1, 1)
        self.free_layout.addWidget(self.dte_to, 1, 1, 1, 1)

        self.button_layout.addWidget(self.btn_search)
        self.button_layout.addWidget(self.btn_cancel)

        self.main_layout.addLayout(self.table_players_layout)
        self.main_layout.addWidget(self.tab_select_date)
        self.main_layout.addLayout(self.button_layout)

    def setup_connections(self):
        self.cbx_type_period.currentIndexChanged.connect(self.update_cbx_choice_period)
        self.btn_search.clicked.connect(self.dispatch_action)
        self.btn_cancel.clicked.connect(self.close)

    def update_cbx_choice_period(self):
        """Met à jour les éléments de la combobox choice_period en fonction
        de l'élément sélectionné dans le combobox type_period."""
        self.cbx_choice_period.clear()
        match self.cbx_type_period.currentText():
            case "Mois":
                self.cbx_choice_period.addItems(period_dict["month"])
            case "Trimestre":
                self.cbx_choice_period.addItems(period_dict["quarter"])
            case "Semestre":
                self.cbx_choice_period.addItems(period_dict["semester"])

    def dispatch_action(self):
        """Au clic sur le bouton Rechercher, lance la méthode correspondante à la page
        active. Emet la date de début et fin au format datetime"""
        match self.tab_select_date.currentIndex():
            case 0:
                self.year_date()
            case 1:
                self.period_date()
            case 2:
                self.free_date()

        print(self.start_date, self.end_date, sep="\n")

    def year_date(self):
        """Détermine la date de début et de fin d'une année fixe ou sur les
        douze derniers mois."""
        if self.radio_year.isChecked():
            year_ = int(self.cbx_year.currentText())
            self.start_date = datetime(year_, 1, 1, 0, 0, 0)
            self.end_date = datetime(year_, 12, 31, 23, 59, 59)
        else:
            today = datetime.now()
            self.end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
            self.start_date = self.end_date.replace(year=self.end_date.year - 1,
                                                    hour=0,
                                                    minute=0,
                                                    second=0)

    def period_date(self):
        """Détermine la date de début et de fin pour une période présice."""
        self.start_date, self.end_date = get_first_and_last_day_of_period(
            self.cbx_choice_period.currentText(),
            int(self.cbx_year_period.currentText())
        )

    def free_date(self):
        """Récupère la date de début et de fin sélectionnées par l'utilisateur."""
        self.start_date = self.dte_from.dateTime().toPython()
        self.end_date = self.dte_to.dateTime().toPython()
        if self.end_date < self.start_date:
            self.end_date, self.start_date = self.start_date, self.end_date


if __name__ == '__main__':
    from suivi_tarot.api.utils import DATA_FILE
    from suivi_tarot.database.clients import init_bdd

    if not DATA_FILE.exists():
        init_bdd()
    app = QApplication()
    window = SelectDates()
    window.show()
    app.exec()
    # print(get_first_and_last_day_of_period("janvier - juin", 2022))
