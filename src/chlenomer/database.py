import peewee


database = peewee.SqliteDatabase("data/database.sqlite")


class Player(peewee.Model):
    name = peewee.CharField()
    coins = peewee.IntegerField(default=0)
    level = peewee.IntegerField(default=1)
    mined = peewee.BooleanField(default=False)
    bets = peewee.IntegerField(default=0)

    class Meta:
        database = database
