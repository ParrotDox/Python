from enum import Enum
class SelectModes(Enum):
    POINT = 0 #Move only point
    LINE = 1 #Move only lines
    MIXED = 2 #Move everything
class Figures(Enum):
    POINT = 0
    LINE = 1
    CUBE = 2
    MIXED = 3