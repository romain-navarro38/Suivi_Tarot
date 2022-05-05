from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from suivi_tarot.api.utils import COLOR_GRAPH


# noinspection PyAttributeOutsideInit
class GraphWidget(QWidget):
    """Widget pour l'affichage graphique des classements"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure()
        self.ax = self.figure.add_subplot()
        self.parent = parent
        rgb = self.parent.palette().color(QWidget.backgroundRole(self.parent)).toTuple()
        self.figure.set_facecolor((rgb[0]/255, rgb[1]/255, rgb[2]/255))
        self.ax.set_facecolor((rgb[0]/255, rgb[1]/255, rgb[2]/255))
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.canvas = FigureCanvas(self.figure)

    def modify_widgets(self):
        self.figure.set_tight_layout(True)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.canvas)

    def setup_connections(self):
        self.graph = self.parent.refresh_graph.connect(self.plot)

    def plot(self, data, point, window):
        """Génération des courbes"""
        self.ax.clear()
        self.ax.set_xlim(0, point)
        self.ax.set_xticks(list(range(point)))
        for i, (player, score) in enumerate(data.items()):
            if window == "table":
                self.ax.plot(score, label=player, color=COLOR_GRAPH[i])
            elif window == "ranking":
                self.ax.plot(score, label=player)
                self.ax.annotate(f'{player} ({score[-1]})',
                                 xy=(point - 1, score[-1]),
                                 xytext=(5, 0),
                                 textcoords='offset points')
        # self.ax.legend()
        self.ax.grid(axis="y")
        self.canvas.draw()
