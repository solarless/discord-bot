from playhouse.migrate import BooleanField
from playhouse.migrate import SqliteMigrator
from playhouse.migrate import migrate

from chlenomer.database import database


migrator = SqliteMigrator(database)


def up():
    migrate(
        migrator.drop_column("player", "automated"),
    )


def down():
    migrate(
        migrator.add_column("player", "automated", BooleanField(default=False)),
    )
