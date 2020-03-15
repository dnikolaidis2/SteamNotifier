from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegerField

db = SqliteDatabase('db/mods.db')


class Mod(Model):
    steam_id = IntegerField(unique=False)
    name = CharField(null=False)
    last_updated = DateTimeField(null=False)
    discord_channel_id = IntegerField(null=False)

    def __str__(self):
        return f"Mod[{self.steam_id}, {self.name}, {self.last_updated}]"

    class Meta:
        database = db
