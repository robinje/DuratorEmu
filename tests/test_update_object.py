import unittest

from durator.world.handlers.game.player_login import *


class TestUpdateObject(unittest.TestCase):
    def test_add(self):
        """add, simple fields add cases"""
        update = ObjectUpdate()

        update.add(UpdateFieldObject.GUID, 0xDEAD)
        self.assertEqual(update.mask_blocks, [0b00011])
        self.assertEqual(len(update.update_blocks), 1)

        update.add(UpdateFieldObject.SCALE_X, 1.0)
        self.assertEqual(update.mask_blocks, [0b10011])
        self.assertEqual(len(update.update_blocks), 2)

        update.add(UpdateFieldObject.TYPE, 0x19)
        self.assertEqual(update.mask_blocks, [0b10111])
        self.assertEqual(len(update.update_blocks), 3)

    def test_to_bytes(self):
        """to_bytes, with a few simple fields"""
        update = ObjectUpdate()
        update.add(UpdateFieldObject.GUID, 0xDEAD)
        update.add(UpdateFieldObject.SCALE_X, 1.0)
        update.add(UpdateFieldObject.TYPE, 0x19)
        data = update.to_bytes()
        expected = (
            int.to_bytes(0b10111, 4, "little") + b"\xAD\xDE\x00\x00\x00\x00\x00\x00" + b"\x00\x00\x80\x3F" + b"\x19\x00\x00\x00"
        )
        self.assertEqual(data, expected)
