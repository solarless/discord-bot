from playhouse.migrate import IntegerField
from playhouse.migrate import SqliteMigrator
from playhouse.migrate import migrate

from chlenomer.database import database


migrator = SqliteMigrator(database)


def up():
    migrate(
        migrator.drop_column("player", "rate"),
        migrator.add_column("player", "level", IntegerField(default=0)),
    )


def down():
    migrate(
        migrator.drop_column("player", "level"),
        migrator.add_column("player", "rate", IntegerField(default=10)),
    )
