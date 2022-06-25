import hashlib
import uuid
from pathlib import Path
from random import choice

CUR_FILE = Path(__file__)
ROOT_FOLDER = CUR_FILE.parent.parent.parent
DATA_FILE = ROOT_FOLDER / "db.sqlite3"
SETTINGS_FILE = ROOT_FOLDER / "settings.json"
IMAGE_FOLDER = ROOT_FOLDER / "ressource" / "image"

HEADER_3_4 = ["Preneur",
              "Contrat",
              "Bout",
              "Point",
              "Poignée",
              "Petit au bout",
              "Petit Chelem",
              "Grand Chelem"]

HEADER_5 = ["Preneur",
            "Contrat",
            "Bout",
            "Point",
            "Tête",
            "Appelé",
            "Poignée",
            "Petit au bout",
            "Petit Chelem",
            "Grand Chelem"]

HEADER_6 = ["PNJ",
            "Preneur",
            "Contrat",
            "Bout",
            "Point",
            "Tête",
            "Appelé",
            "Poignée",
            "Petit au bout",
            "Petit Chelem",
            "Grand Chelem"]

HEAD = ["R \u2665",  # cœur
        "R \u2666",  # carreau
        "R \u2663",  # trefle
        "R \u2660",  # pique
        "D \u2665",
        "D \u2666",
        "D \u2663",
        "D \u2660"]

PLAYERS = ["Romain", "Ludo", "Emeline", "Eddy", "Aurore"]

COLOR_DEFAULT = ['#0000ff', '#ff8c00', '#008000', '#ff0000', '#800080', '#800000']

COLOR_PREDEFINED = {'White': '#ffffff',
                    'Ivory': '#fffff0',
                    'Light yellow': '#ffffe0',
                    'Yellow': '#ffff00',
                    'Snow': '#fffafa',
                    'Floral white': '#fffaf0',
                    'Lemon chiffon': '#fffacd',
                    'Cornsilk': '#fff8dc',
                    'Sea shell': '#fff5ee',
                    'Lavender blush': '#fff0f5',
                    'Papaya whip': '#ffefd5',
                    'Blanched almond': '#ffebcd',
                    'Misty rose': '#ffe4e1',
                    'Bisque': '#ffe4c4',
                    'Moccasin': '#ffe4b5',
                    'Navajo white': '#ffdead',
                    'Peach puff': '#ffdab9',
                    'Gold': '#ffd700',
                    'Pink': '#ffc0cb',
                    'Light pink': '#ffb6c1',
                    'Orange': '#ffa500',
                    'Light salmon': '#ffa07a',
                    'Dark orange': '#ff8c00',
                    'Coral': '#ff7f50',
                    'Hot pink': '#ff69b4',
                    'Tomato': '#ff6347',
                    'Orange red': '#ff4500',
                    'Deep pink': '#ff1493',
                    'Fuchsia': '#ff00ff',
                    'Red': '#ff0000',
                    'Old lace': '#fdf5e6',
                    'Light golden rod yellow': '#fafad2',
                    'Linen': '#faf0e6',
                    'Antique white': '#faebd7',
                    'Salmon': '#fa8072',
                    'Ghost white': '#f8f8ff',
                    'Mint cream': '#f5fffa',
                    'White smoke': '#f5f5f5',
                    'Beige': '#f5f5dc',
                    'Wheat': '#f5deb3',
                    'Sandy brown': '#f4a460',
                    'Azure': '#f0ffff',
                    'Honey dew': '#f0fff0',
                    'Alice blue': '#f0f8ff',
                    'Khaki': '#f0e68c',
                    'Light coral': '#f08080',
                    'Pale golden rod': '#eee8aa',
                    'Violet': '#ee82ee',
                    'Dark salmon': '#e9967a',
                    'Lavender': '#e6e6fa',
                    'Light cyan': '#e0ffff',
                    'Burly wood': '#deb887',
                    'Plum': '#dda0dd',
                    'Gainsboro': '#dcdcdc',
                    'Crimson': '#dc143c',
                    'Pale violet red': '#db7093',
                    'Golden rod': '#daa520',
                    'Orchid': '#da70d6',
                    'Thistle': '#d8bfd8',
                    'Light grey': '#d3d3d3',
                    'Tan': '#d2b48c',
                    'Chocolate': '#d2691e',
                    'Peru': '#cd853f',
                    'Indian red': '#cd5c5c',
                    'Medium violet red': '#c71585',
                    'Silver': '#c0c0c0',
                    'Dark khaki': '#bdb76b',
                    'Rosy brown': '#bc8f8f',
                    'Medium orchid': '#ba55d3',
                    'Dark golden rod': '#b8860b',
                    'Fire brick': '#b22222',
                    'Powder blue': '#b0e0e6',
                    'Light steel blue': '#b0c4de',
                    'Pale turquoise': '#afeeee',
                    'Green yellow': '#adff2f',
                    'Light blue': '#add8e6',
                    'Dark grey': '#a9a9a9',
                    'Brown': '#a52a2a',
                    'Sienna': '#a0522d',
                    'Yellow green': '#9acd32',
                    'Dark orchid': '#9932cc',
                    'Pale green': '#98fb98',
                    'Dark violet': '#9400d3',
                    'Medium purple': '#9370db',
                    'Light green': '#90ee90',
                    'Dark sea green': '#8fbc8f',
                    'Saddle brown': '#8b4513',
                    'Dark magenta': '#8b008b',
                    'Dark red': '#8b0000',
                    'Blue violet': '#8a2be2',
                    'Light sky blue': '#87cefa',
                    'Sky blue': '#87ceeb',
                    'Grey': '#808080',
                    'Olive': '#808000',
                    'Purple': '#800080',
                    'Maroon': '#800000',
                    'Aquamarine': '#7fffd4',
                    'Chartreuse': '#7fff00',
                    'Lawn green': '#7cfc00',
                    'Medium slate blue': '#7b68ee',
                    'Light slate grey': '#778899',
                    'Slate grey': '#708090',
                    'Olive drab': '#6b8e23',
                    'Slate blue': '#6a5acd',
                    'Dim grey': '#696969',
                    'Medium aqua marine': '#66cdaa',
                    'Rebecca purple': '#663399',
                    'Cornflower blue': '#6495ed',
                    'Cadet blue': '#5f9ea0',
                    'Dark olive green': '#556b2f',
                    'Indigo': '#4b0082',
                    'Medium turquoise': '#48d1cc',
                    'Dark slate blue': '#483d8b',
                    'Steel blue': '#4682b4',
                    'Royal blue': '#4169e1',
                    'Turquoise': '#40e0d0',
                    'Medium sea green': '#3cb371',
                    'Lime green': '#32cd32',
                    'Dark slate gray': '#2f4f4f',
                    'Sea green': '#2e8b57',
                    'Forest green': '#228b22',
                    'Light sea green': '#20b2aa',
                    'Dodger blue': '#1e90ff',
                    'Midnight blue': '#191970',
                    'Cyan': '#00ffff',
                    'Spring green': '#00ff7f',
                    'Lime': '#00ff00',
                    'Medium spring green': '#00fa9a',
                    'Dark turquoise': '#00ced1',
                    'Deep sky blue': '#00bfff',
                    'Dark cyan': '#008b8b',
                    'Teal': '#008080',
                    'Green': '#008000',
                    'Dark green': '#006400',
                    'Blue': '#0000ff',
                    'Medium blue': '#0000cd',
                    'Dark blue': '#00008b',
                    'Navy': '#000080',
                    'Black': '#000000'}


def convert_rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Returns rgb values in hexadecimal format"""
    return f'#{hex(rgb[0])[2:].zfill(2)}{hex(rgb[1])[2:].zfill(2)}{hex(rgb[2])[2:].zfill(2)}'


def convert_hex_to_rgb(hexa: str) -> tuple[int, int, int]:
    """Returns rgb values in int format"""
    return int(f'0x{hexa[1:3]}', 16), int(f'0x{hexa[3:5]}', 16), int(f'0x{hexa[5:]}', 16)


def get_random_item_with_constraint(list_str: list[str], prohibited_item: str) -> str:
    # sourcery skip: use-assigned-variable
    """Retourne un élément choisi aléatoirement dans une liste de str
    avec la contrainte d'être différent d'un élément en particulier"""
    item = prohibited_item
    while prohibited_item == item:
        item = choice(list_str)
    return item


def generate_salt() -> str:
    """Retourne une chaîne de caractères unique"""
    return str(uuid.uuid4())


def hashage_password(password: str, salt: str = "") -> tuple[str, str]:
    """Génére le hash d'une chaîne de caractères en lui ajoutant un sel.
    Retourne le hash et le sel utilisé"""
    if not salt:
        salt = generate_salt()
    hash_ = hashlib.sha256(bytes((password + salt).encode('utf-8'))).hexdigest()
    return hash_, salt


def move_database(path: str):
    """Déplace la base de données créée dans le dossier projet vers le dossier
    sélectionné par l'utilisateur"""
    DATA_FILE.rename(Path(path) / DATA_FILE.name)


if __name__ == "__main__":
    print(hashage_password("romain"))
