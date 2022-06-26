from enum import Enum

from durator.world.game.movement import Movement, MovementFlags
from durator.world.game.object.object_fields import UnitField
from durator.world.game.object.type.base_object import BaseObject


class UnitPower(Enum):

    MANA = 0
    RAGE = 1
    FOCUS = 2
    ENERGY = 3
    HAPPINESS = 4


class UnitStat(Enum):

    STRENGTH = 0
    AGILITY = 1
    STAMINA = 2
    INTELLECT = 3
    SPIRIT = 4


class Bytes0Mask(Enum):

    RACE = 0x000000FF
    CLASS = 0x0000FF00
    GENDER = 0x00FF0000
    UNK = 0xFF000000


DEFAULT_SPEEDS = {"walk": 2.5, "run": 7.0, "run_bw": 4.5, "swim": 4.7222223, "swim_bw": 2.5, "turn": 3.141593}


class Unit(BaseObject):
    """A Unit is a BaseObject that can move, attack, etc.

    The movement attribute is the most recently recorded movement block; to
    access this Unit's position, you should use BaseObject.position.
    """

    def __init__(self):
        super().__init__()
        self.movement = Movement()
        self.speeds = DEFAULT_SPEEDS.copy()

    def get_race(self):
        unit_bytes_0 = self._get_bytes_0()
        return unit_bytes_0 & Bytes0Mask.RACE.value

    def get_class(self):
        unit_bytes_0 = self._get_bytes_0()
        return (unit_bytes_0 & Bytes0Mask.CLASS.value) >> 8

    def get_gender(self):
        unit_bytes_0 = self._get_bytes_0()
        return (unit_bytes_0 & Bytes0Mask.GENDER.value) >> 16

    def _get_bytes_0(self):
        unit_bytes_0 = self.get(UnitField.BYTES_0)
        return unit_bytes_0 or 0

    def is_falling(self):
        falling_flags = MovementFlags.IS_FALLING.value
        return bool(self.movement.flags & falling_flags)
