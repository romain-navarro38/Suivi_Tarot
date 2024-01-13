from datetime import datetime
from functools import partial

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QMouseEvent, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, \
    QSizePolicy, QLabel, QCommandLinkButton

from suivi_tarot.api.ranking import Ranking
from suivi_tarot.api.utils import IMAGE_FOLDER
from suivi_tarot.window.animated_toggle import AnimatedToggle
from suivi_tarot.window.graph_ranking import GraphWidget
from suivi_tarot.window.select_dates import SelectDates
from suivi_tarot.window.table import LabelScore


def clear_layout(layout):
    """Efface tout widget d'un layout"""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


class CustomLabelToggle(QLabel):
    clicked = Signal()

    def __init__(self, text: str, enabled: bool, position: str):
        super().__init__(text)

        self.setFixedSize(QSize(100, 45))
        self.font = QFont()
        self.font.setPointSize(12)
        self.setFont(self.font)
        self.setBold(enabled)
        if position == "right":
            self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.clicked.emit()

    def setBold(self, enabled: bool) -> None:
        self.font.setBold(enabled)
        self.setFont(self.font)


# noinspection PyAttributeOutsideInit
class RankingWindow(QWidget):

    refresh_graph = Signal(dict, int, str)

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.setWindowTitle("Classement")
        self.init_graph()
        self.showMaximized()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.la_title = QLabel()
        self.graph = GraphWidget(self)
        self.spacer_vertical = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.spacer_horizontal = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.btn_change_period = QCommandLinkButton("Changer de période")
        self.la_classement = CustomLabelToggle("Classement", True, "left")
        self.toggle_view = AnimatedToggle()
        self.la_statistique = CustomLabelToggle("Statistique", False, "right")
        self.btn_quit = QPushButton("Quitter")

    def modify_widgets(self):
        font_title = QFont()
        font_title.setPointSize(16)
        font_title.setBold(True)
        self.la_title.setFont(font_title)
        self.la_title.setAlignment(Qt.AlignCenter)
        self.graph.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.btn_change_period.setIcon(QIcon(QPixmap(IMAGE_FOLDER / "calendar-blue.png")))
        self.btn_change_period.setIconSize(QSize(32, 32))
        self.btn_change_period.setFlat(True)
        self.toggle_view.setFixedSize(self.toggle_view.sizeHint())

    def create_layouts(self):
        self.title_layout = QHBoxLayout()
        self.graph_score_layout = QHBoxLayout()
        self.score_layout = QGridLayout()
        self.score_vertical_layout = QVBoxLayout()
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.title_layout.addWidget(self.btn_change_period)
        self.title_layout.addSpacerItem(self.spacer_horizontal)
        self.title_layout.addWidget(self.la_title)
        self.title_layout.addSpacerItem(self.spacer_horizontal)
        self.title_layout.addWidget(self.la_classement)
        self.title_layout.addWidget(self.toggle_view)
        self.title_layout.addWidget(self.la_statistique)
        self.title_layout.addWidget(self.btn_quit)
        self.essai = QWidget()
        self.essai.setVisible(False)
        self.essai.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.graph_score_layout.addWidget(self.essai)
        self.graph_score_layout.addWidget(self.graph)
        self.score_vertical_layout.addSpacerItem(self.spacer_vertical)
        self.score_vertical_layout.addLayout(self.score_layout)
        self.score_vertical_layout.addSpacerItem(self.spacer_vertical)
        self.graph_score_layout.addLayout(self.score_vertical_layout)
        self.main_layout.addLayout(self.title_layout)
        self.main_layout.addLayout(self.graph_score_layout)

    def setup_connections(self):
        self.btn_change_period.clicked.connect(self.other_search)
        self.la_classement.clicked.connect(partial(self.label_click, "classement"))
        self.toggle_view.stateChanged.connect(self.change_display_label)
        self.la_statistique.clicked.connect(partial(self.label_click, "statistique"))
        self.etat = True
        self.btn_quit.clicked.connect(self.close_)

    def close_(self):
        if self.etat:
            self.graph.setVisible(False)
            self.essai.setVisible(True)
        else:
            self.essai.setVisible(False)
            self.graph.setVisible(True)
        self.etat = not self.etat

    def label_click(self, value: str):
        if value == "classement":
            self.toggle_view.setCheckState(Qt.Unchecked)
        else:
            self.toggle_view.setCheckState(Qt.Checked)

    def change_display_label(self, value: int):
        if value:
            self.la_classement.setBold(False)
            self.la_statistique.setBold(True)
        else:
            self.la_classement.setBold(True)
            self.la_statistique.setBold(False)

    def other_search(self):
        """Ouvre la fenêtre de sélection de dates"""
        self.search = SelectDates()
        self.search.search_parameters.connect(self.update_display)
        self.search.show()

    def update_display(self, start: datetime, end: datetime, table_of: int):
        """Lance les mises à jour d'affichage : graph, score et titre"""
        self.update_graph(start, end, table_of)
        clear_layout(self.score_layout)
        self.update_score()
        self.update_title(start, end, table_of)

    def update_graph(self, start: datetime, end: datetime, table_of: int):
        """Charge le graphique"""
        self.rank = Ranking(start, end, table_of)
        rank: dict[list[str]] = self.rank.ranking.to_dict(orient="list")
        for liste in rank.values():
            liste.insert(0, 0)
        self.refresh_graph.emit(rank, self.rank.number_of_game + 1, "ranking")

    def update_score(self):
        """Affiche les scores triés"""
        self.last_ranking = sorted(self.get_last_ranking(), key=lambda v: v[1], reverse=True)
        self.lbl_player = [LabelScore(f"{player[0]} :", "") for player in self.last_ranking]
        self.lbl_score = [LabelScore(f"{player[1]}", "form") for player in self.last_ranking]
        for i in range(len(self.rank.distinct_player)):
            self.score_layout.addWidget(self.lbl_player[i], i, 0)
            self.score_layout.addWidget(self.lbl_score[i], i, 1)

    def update_title(self, start: datetime, end: datetime, table_of: int):
        """Mise à jour du titre"""
        start = start.strftime("%d/%m/%Y")
        end = end.strftime("%d/%m/%Y")
        self.la_title.setText(f"Du {start} au {end} - Table de {table_of} joueurs")

    def init_graph(self):
        """Au démarrage de la fenêtre, lance le chargement des données
        pour l'année en cours"""
        table_of = 5
        year = datetime.now().year
        start = datetime(year, 1, 1, 0, 0, 0)
        end = datetime(year, 12, 31, 23, 59, 59)
        self.update_display(start, end, table_of)

    def get_last_ranking(self) -> list[tuple[str, int]]:
        """Récupération du dernier score de chaque joueur"""
        return [(nickname, score.iloc[-1]) for (nickname, score) in self.rank.ranking.iteritems()]


if __name__ == '__main__':
    app = QApplication()
    window = RankingWindow()
    window.show()
    app.exec()
