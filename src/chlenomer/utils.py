import datetime
import time

import discord
import schedule

from chlenomer.database import Player


def check_auth(name):
    player: Player = Player.get_or_none(Player.name == name)
    if player is None:
        return False
    return True


async def ask_to_create_account(context: discord.ApplicationContext):
    await context.respond(
        ":red_square: Я тебя не знаю <:Concerned:1126355619562131487>\n"
        "Напиши **/start** чтобы создать аккаунт"
    )


def scheduling_tick():
    while True:
        schedule.run_pending()
        time.sleep(2)


def get_minutes_to_nearest_reset():
    now = datetime.datetime.now()
    if now.minute >= 0 and now.minute < 30:
        return 30 - now.minute
    return 60 - now.minute
