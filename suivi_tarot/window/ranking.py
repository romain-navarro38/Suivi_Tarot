from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout

from suivi_tarot.api.ranking import Ranking
from suivi_tarot.window.graph_ranking import GraphWidget
from suivi_tarot.window.select_dates import SelectDates

# noinspection PyAttributeOutsideInit
class RankingWindow(QWidget):

    refresh_graph = Signal(dict, int, str)

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.setWindowTitle("Classement")
        self.showMaximized()
        self.init_graph()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.graph = GraphWidget(self)
        self.btn_change_period = QPushButton("Autre période")
        self.btn_statistics = QPushButton("Voir les statistiques")
        self.btn_quit = QPushButton("Quitter")

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.button_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.button_layout.addWidget(self.btn_change_period)
        self.button_layout.addWidget(self.btn_statistics)
        self.button_layout.addWidget(self.btn_quit)
        self.main_layout.addWidget(self.graph)
        self.main_layout.addLayout(self.button_layout)

    def setup_connections(self):
        self.btn_quit.clicked.connect(self.close)
        self.btn_change_period.clicked.connect(self.other_search)

    def other_search(self):
        self.search = SelectDates()
        self.search.search_parameters.connect(self.display_graph)
        self.search.show()

    def display_graph(self, start: datetime, end: datetime, table_of: int):
        self.rank = Ranking(start, end, table_of)
        rank = self.rank.ranking.to_dict(orient="list")
        for liste in rank.values():
            liste.insert(0, 0)
        self.refresh_graph.emit(rank, self.rank.number_of_game + 1, "ranking")

    def init_graph(self):
        table_of = 5
        year = datetime.now().year
        start = datetime(year, 1, 1, 0, 0, 0)
        end = datetime(year, 12, 31, 23, 59, 59)
        self.display_graph(start, end, table_of)


if __name__ == '__main__':
    app = QApplication()
    window = RankingWindow()
    window.show()
    app.exec()
