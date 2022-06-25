from functools import partial

from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QRadioButton, QSlider, QLabel, QPushButton, \
    QComboBox, QGroupBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QSize

from suivi_tarot.api.utils import COLOR_DEFAULT, COLOR_PREDEFINED, convert_hex_to_rgb, convert_rgb_to_hex
from suivi_tarot.api.settings import get_player_color_graph, set_player_color_graph


def change_label_number(label, new_value):
    label.setNum(new_value)


def search_color_predefined(hexa):
    return next((name for name, color_hexa in COLOR_PREDEFINED.items() if color_hexa == hexa), "")


# noinspection PyAttributeOutsideInit
class ColorPlayerWindow(QWidget):
    """Window for defining the colors associated withplayers in the follow-up of a game in progress"""
    def __init__(self):
        super().__init__()

        self.resize(340, 284)
        self.setMinimumSize(QSize(340, 0))
        self.color_graph = get_player_color_graph()
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        self.move_sliders(0)

    def create_widgets(self):
        self.lbl_sep = QLabel("")

        self.gb_radiobutton = QGroupBox()
        self.rad_player1 = QRadioButton("Joueur1")
        self.rad_player2 = QRadioButton("Joueur2")
        self.rad_player3 = QRadioButton("Joueur3")
        self.rad_player4 = QRadioButton("Joueur4")
        self.rad_player5 = QRadioButton("Joueur5")
        self.rad_player6 = QRadioButton("Joueur6")

        self.lbl_red = QLabel("Rouge")
        self.lbl_green = QLabel("Vert")
        self.lbl_blue = QLabel("Bleu")
        self.sl_red = QSlider()
        self.sl_green = QSlider()
        self.sl_blue = QSlider()
        self.lbl_nb_red = QLabel("0")
        self.lbl_nb_green = QLabel("0")
        self.lbl_nb_blue = QLabel("0")

        self.lbl_predefined = QLabel("Prédéfinie")
        self.cbx_predefined = QComboBox()

        self.btn_default = QPushButton("Couleurs par défaut")

        self.btn_valid = QPushButton("Valider")
        self.btn_close = QPushButton("Fermer")

    def modify_widgets(self):
        self.lbl_sep.setMinimumSize(QSize(10, 0))
        self.lbl_sep.setMaximumSize(QSize(10, 16777215))

        self.gb_radiobutton.setStyleSheet("border: none")
        font_rad = QFont()
        font_rad.setPointSize(16)
        font_rad.setBold(True)
        self.rad_player1.setFont(font_rad)
        self.rad_player2.setFont(font_rad)
        self.rad_player3.setFont(font_rad)
        self.rad_player4.setFont(font_rad)
        self.rad_player5.setFont(font_rad)
        self.rad_player6.setFont(font_rad)
        self.rad_player1.setLayoutDirection(Qt.RightToLeft)
        self.rad_player2.setLayoutDirection(Qt.RightToLeft)
        self.rad_player3.setLayoutDirection(Qt.RightToLeft)
        self.rad_player1.setChecked(True)
        self.colorize_player_labels(self.color_graph)

        font_label = QFont()
        font_label.setBold(True)
        self.lbl_red.setFont(font_label)
        self.lbl_green.setFont(font_label)
        self.lbl_blue.setFont(font_label)
        self.lbl_red.setMaximumSize(QSize(58, 16777215))
        self.lbl_green.setMaximumSize(QSize(58, 16777215))
        self.lbl_blue.setMaximumSize(QSize(58, 16777215))
        self.lbl_red.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.lbl_green.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.lbl_blue.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.sl_red.setStyleSheet(u"QSlider::handle:horizontal {background-color: red}")
        self.sl_red.setMaximum(255)
        self.sl_red.setOrientation(Qt.Horizontal)
        self.sl_red.setTickPosition(QSlider.NoTicks)
        self.sl_green.setStyleSheet(u"QSlider::handle:horizontal {background-color: green}")
        self.sl_green.setMaximum(255)
        self.sl_green.setOrientation(Qt.Horizontal)
        self.sl_green.setTickPosition(QSlider.NoTicks)
        self.sl_blue.setStyleSheet(u"QSlider::handle:horizontal {background-color: blue}")
        self.sl_blue.setMaximum(255)
        self.sl_blue.setOrientation(Qt.Horizontal)
        self.sl_blue.setTickPosition(QSlider.NoTicks)

        self.lbl_nb_red.setFont(font_label)
        self.lbl_nb_green.setFont(font_label)
        self.lbl_nb_blue.setFont(font_label)
        self.lbl_nb_red.setAlignment(Qt.AlignCenter)
        self.lbl_nb_green.setAlignment(Qt.AlignCenter)
        self.lbl_nb_blue.setAlignment(Qt.AlignCenter)
        self.lbl_nb_red.setMaximumSize(QSize(58, 16777215))
        self.lbl_nb_green.setMaximumSize(QSize(58, 16777215))
        self.lbl_nb_blue.setMaximumSize(QSize(58, 16777215))

        self.lbl_predefined.setMaximumSize(QSize(58, 16777215))
        self.lbl_predefined.setFont(font_label)
        self.lbl_predefined.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.cbx_predefined.addItem("")
        self.cbx_predefined.addItems(COLOR_PREDEFINED.keys())

        self.btn_valid.setMinimumSize(QSize(0, 40))
        self.btn_close.setMinimumSize(QSize(0, 40))

    def create_layouts(self):
        self.radio_layout = QGridLayout(self.gb_radiobutton)
        self.main_layout = QGridLayout(self)

    def add_widgets_to_layouts(self):
        self.radio_layout.addWidget(self.rad_player1, 0, 0, 1, 2)
        self.radio_layout.addWidget(self.lbl_sep, 0, 2, 1, 1)
        self.radio_layout.addWidget(self.rad_player2, 1, 0, 1, 2)
        self.radio_layout.addWidget(self.rad_player3, 2, 0, 1, 2)
        self.radio_layout.addWidget(self.rad_player4, 0, 3, 1, 2)
        self.radio_layout.addWidget(self.rad_player5, 1, 3, 1, 2)
        self.radio_layout.addWidget(self.rad_player6, 2, 3, 1, 2)
        self.main_layout.addWidget(self.gb_radiobutton, 0, 0, 3, 5)
        self.main_layout.addWidget(self.lbl_red, 3, 0, 1, 1)
        self.main_layout.addWidget(self.lbl_green, 4, 0, 1, 1)
        self.main_layout.addWidget(self.lbl_blue, 5, 0, 1, 1)
        self.main_layout.addWidget(self.sl_red, 3, 1, 1, 3)
        self.main_layout.addWidget(self.sl_green, 4, 1, 1, 3)
        self.main_layout.addWidget(self.sl_blue, 5, 1, 1, 3)
        self.main_layout.addWidget(self.lbl_nb_red, 3, 4, 1, 1)
        self.main_layout.addWidget(self.lbl_nb_green, 4, 4, 1, 1)
        self.main_layout.addWidget(self.lbl_nb_blue, 5, 4, 1, 1)
        self.main_layout.addWidget(self.lbl_predefined, 6, 0, 1, 1)
        self.main_layout.addWidget(self.cbx_predefined, 6, 1, 1, 3)
        self.main_layout.addWidget(self.btn_default, 9, 1, 1, 3)
        self.main_layout.addWidget(self.btn_valid, 10, 1, 1, 1)
        self.main_layout.addWidget(self.btn_close, 10, 3, 1, 1)

    def setup_connections(self):
        self.rad_player1.clicked.connect(partial(self.move_sliders, 0))
        self.rad_player2.clicked.connect(partial(self.move_sliders, 1))
        self.rad_player3.clicked.connect(partial(self.move_sliders, 2))
        self.rad_player4.clicked.connect(partial(self.move_sliders, 3))
        self.rad_player5.clicked.connect(partial(self.move_sliders, 4))
        self.rad_player6.clicked.connect(partial(self.move_sliders, 5))
        self.sl_red.valueChanged.connect(partial(self.update_color, self.lbl_nb_red))
        self.sl_green.valueChanged.connect(partial(self.update_color, self.lbl_nb_green))
        self.sl_blue.valueChanged.connect(partial(self.update_color, self.lbl_nb_blue))
        self.cbx_predefined.currentIndexChanged.connect(self.predefined)
        self.btn_default.clicked.connect(self.default_color)
        self.btn_valid.clicked.connect(self.save_change)
        self.btn_close.clicked.connect(self.close)

    def update_color(self, label_count: QLabel, new_value):
        """Modification of the interface after interaction on one of the sliders"""
        change_label_number(label_count, new_value)
        hexa = self.change_color_radiobutton()
        name_color = search_color_predefined(hexa)
        self.change_combobox(name_color)

    def change_color_radiobutton(self) -> str:
        """Changes the color of the selected radiobutton from the position of the sliders"""
        radiobutton, number = self.radiobutton_checked()
        hexa = convert_rgb_to_hex((self.sl_red.value(), self.sl_green.value(), self.sl_blue.value()))
        self.color_graph[number] = hexa
        radiobutton.setStyleSheet(f"color: {hexa};")
        return hexa

    def predefined(self):
        """Changes the color of the selected radio button from the selected preset color"""
        if hexa := COLOR_PREDEFINED.get(self.cbx_predefined.currentText(), ""):
            radiobutton, number = self.radiobutton_checked()
            self.color_graph[number] = hexa
            radiobutton.setStyleSheet(f"color: {hexa};")
            self.move_sliders(number)

    def change_combobox(self, name: str):
        """Changes the item displayed in the combobox"""
        self.cbx_predefined.setCurrentText(name)

    def colorize_player_labels(self, colors: list):
        """Applies the colors in the list to each radio button"""
        self.rad_player1.setStyleSheet(f"color: {colors[0]};")
        self.rad_player2.setStyleSheet(f"color: {colors[1]};")
        self.rad_player3.setStyleSheet(f"color: {colors[2]};")
        self.rad_player4.setStyleSheet(f"color: {colors[3]};")
        self.rad_player5.setStyleSheet(f"color: {colors[4]};")
        self.rad_player6.setStyleSheet(f"color: {colors[5]};")

    def move_sliders(self, player_number: int):
        """Changes the location of the cursors according to the selected player"""
        color_hex = self.color_graph[player_number]
        self.sl_red.setValue(convert_hex_to_rgb(color_hex)[0])
        self.sl_green.setValue(convert_hex_to_rgb(color_hex)[1])
        self.sl_blue.setValue(convert_hex_to_rgb(color_hex)[2])

    def default_color(self):
        """Applies the default color list"""
        self.colorize_player_labels(COLOR_DEFAULT)
        self.color_graph = COLOR_DEFAULT.copy()
        self.move_sliders(self.radiobutton_checked()[1])

    def radiobutton_checked(self) -> tuple[QRadioButton, int]:
        """Returns the selected radio button and its number"""
        widgets = self.gb_radiobutton.children()
        radioButtons = [widget for widget in widgets if isinstance(widget, QRadioButton)]
        for radiobutton in radioButtons:
            if radiobutton.isChecked():
                return radiobutton, int(radiobutton.text()[-1]) - 1

    def save_change(self):
        """Save the new custom color list and close the window"""
        set_player_color_graph(default=False, color_list=self.color_graph)
        self.close()


if __name__ == '__main__':
    app = QApplication()
    window = ColorPlayerWindow()
    window.show()
    app.exec()
