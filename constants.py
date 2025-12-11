"""Constants and enumerations for the Missionaries and Cannibals game."""

from enum import Enum

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 545
FPS = 60

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (220, 53, 69)
COLOR_GREEN = (40, 167, 69)
COLOR_SELECTED = (255, 255, 0)
COLOR_TEXT_BG = (255, 255, 255, 180)

LEFT_BANK_X = 120
RIGHT_BANK_X = 880
BOAT_LEFT_X = 320
BOAT_RIGHT_X = 680
BOAT_Y = 350
CHARACTER_Y_TOP = 180
CHARACTER_Y_BOTTOM = 300
CHARACTER_SIZE = 120
BOAT_WIDTH = 230
BOAT_HEIGHT = 180

BOAT_SPEED = 3
WOBBLE_SPEED = 0.15
WOBBLE_AMOUNT = 8
EATING_DURATION = 2.0

MISSIONARY_IMAGE = "assets/missionary.png"
CANNIBAL_IMAGE = "assets/cannibal.png"
BACKGROUND_IMAGE = "assets/background.png"
BOAT_IMAGE = "assets/boat.png"


class BoatPosition(Enum):
    """Enumeration for boat position on the river."""
    LEFT = 0
    RIGHT = 1


class GameScreen(Enum):
    """Enumeration for game screen states."""
    WELCOME = 0
    PLAYING = 1
    EATING = 2
    WON = 3
    LOST = 4
