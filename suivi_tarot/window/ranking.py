from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, \
    QSizePolicy, QLabel

from suivi_tarot.api.ranking import Ranking
from suivi_tarot.window.graph_ranking import GraphWidget
from suivi_tarot.window.select_dates import SelectDates
from suivi_tarot.window.table import LabelScore


def clear_layout(layout):
    """Efface tout widget d'un layout"""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


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
        self.title = QLabel()
        self.graph = GraphWidget(self)
        self.spacer_low = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.btn_change_period = QPushButton("Autre période")
        self.btn_statistics = QPushButton("Voir les statistiques")
        self.btn_quit = QPushButton("Quitter")

    def modify_widgets(self):
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setAlignment(Qt.AlignCenter)
        self.graph.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

    def create_layouts(self):
        self.graph_score_layout = QHBoxLayout()
        self.score_layout = QGridLayout()
        self.score_vertical_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.graph_score_layout.addWidget(self.graph)
        self.score_vertical_layout.addLayout(self.score_layout)
        self.score_vertical_layout.addSpacerItem(self.spacer_low)
        self.graph_score_layout.addLayout(self.score_vertical_layout)
        self.button_layout.addWidget(self.btn_change_period)
        self.button_layout.addWidget(self.btn_statistics)
        self.button_layout.addWidget(self.btn_quit)
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.graph_score_layout)
        self.main_layout.addLayout(self.button_layout)

    def setup_connections(self):
        self.btn_quit.clicked.connect(self.close)
        self.btn_change_period.clicked.connect(self.other_search)

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
        self.title.setText(f"Du {start} au {end} - Table de {table_of} joueurs")

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
