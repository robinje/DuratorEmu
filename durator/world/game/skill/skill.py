from peewee import ForeignKeyField, IntegerField, Model

from durator.db.database import DB
from durator.world.game.character.character_data import CharacterData


class Skill(Model):

    character = ForeignKeyField(CharacterData)
    ident = IntegerField()
    level = IntegerField(default=0)
    stat_level = IntegerField(default=0)

    class Meta:
        database = DB
