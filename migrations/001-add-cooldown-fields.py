from playhouse.migrate import BooleanField
from playhouse.migrate import IntegerField
from playhouse.migrate import SqliteMigrator
from playhouse.migrate import migrate

from chlenomer.database import database


migrator = SqliteMigrator(database)


def up():
    migrate(
        migrator.add_column("player", "mined", BooleanField(default=False)),
        migrator.add_column("player", "bets", IntegerField(default=0)),
    )


def down():
    migrate(
        migrator.drop_column("player", "mined"),
        migrator.drop_column("player", "bets"),
    )
