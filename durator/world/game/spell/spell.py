from peewee import ForeignKeyField, IntegerField, Model

from durator.db.database import DB
from durator.world.game.character.character_data import CharacterData


class Spell(Model):

    character = ForeignKeyField(CharacterData)
    ident = IntegerField()

    class Meta:
        database = DB
