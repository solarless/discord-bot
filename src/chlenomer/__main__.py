import os
import random
import threading

import discord
import schedule

from chlenomer.database import Player
from chlenomer.game import LEVELS_TO_RATES
from chlenomer.game import LEVEL_PRICES
from chlenomer.game import MAX_BETS_PER_COOLDOWN
from chlenomer.game import mine_coins
from chlenomer.game import reset_cooldowns
from chlenomer.utils import ask_to_create_account
from chlenomer.utils import check_auth
from chlenomer.utils import get_minutes_to_nearest_reset
from chlenomer.utils import scheduling_tick


DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")


bot = discord.Bot()


@bot.command()
async def ping(context: discord.ApplicationContext):
    await context.respond("<:awwlol:1128809249816989707>")


@bot.command()
async def start(context: discord.ApplicationContext):
    name = context.author.name

    player = Player.get_or_none(Player.name == name)
    if player is not None:
        return await context.respond(":red_square: Я тебя уже знаю <:Concerned:1126355619562131487>")

    Player.create(name=name)
    await context.respond(":memo: Приятно познакомиться <:KKomrade:1126281320105001010>")


@bot.command()
async def mine(context: discord.ApplicationContext):
    player: Player = Player.get_or_none(Player.name == context.author.name)
    if player is None:
        return await ask_to_create_account(context)

    if player.mined:
        minutes_to_reset = get_minutes_to_nearest_reset()
        return await context.respond(
            ":red_square: Майнить можно только раз в пол часа <:Concerned:1126355619562131487>\n"
            f"Возвращайся через {minutes_to_reset} минут"
        )

    amount = mine_coins(player)

    await context.respond(f":pick: Ты намайнил {amount} ({player.coins}) <:chlenocoin:1129537623480881295>")


@bot.command()
async def upgrade(context: discord.ApplicationContext):
    player: Player = Player.get_or_none(Player.name == context.author.name)
    if player is None:
        return await ask_to_create_account(context)

    level = player.level
    if level == 5:
        return await context.respond(":red_square: Ты уже достиг максимального уровня <:awwlol:1128809249816989707>")

    price = LEVEL_PRICES[level+1]
    if player.coins < price:
        return await context.respond(
            ":red_square: У тебя нет таких денег <:Concerned:1126355619562131487>\n"
            f"Улучшение до {level+1} уровня стоит {price} <:chlenocoin:1129537623480881295>"
        )

    player.level += 1
    player.coins -= price
    player.save()

    await context.respond(
        f":tools: Ты апнул {level+1} уровень <:awwlol:1128809249816989707>\n"
        f"Теперь твоя з/п {LEVELS_TO_RATES[player.level]} <:chlenocoin:1129537623480881295>"
    )


@bot.command()
@discord.option(
    name="amount",
    type=int,
    required=True,
)
async def bet(context: discord.ApplicationContext, amount: int):
    player: Player = Player.get_or_none(Player.name == context.author.name)
    if player is None:
        return await ask_to_create_account(context)

    if player.level < 3:
        return await context.respond(":red_square: Сначала надо апнуть 3 лвл <:Clueless:1126355741528297535>")

    minutes_to_reset = get_minutes_to_nearest_reset()
    if player.bets >= MAX_BETS_PER_COOLDOWN:
        return await context.respond(
            ":red_square: Ты же сейчас все деньги проебёшь <:Concerned:1126355619562131487>\n"
            f"Возвращайся через {minutes_to_reset} минут"
        )

    if amount <= 0:
        return await context.respond(":red_square: Ты долбоёб? <:chel:1124482608420622416>")

    if player.coins < amount:
        return await context.respond(":red_square: У тебя нет таких денег <:Concerned:1126355619562131487>")

    won = bool(random.randint(0, 1))
    if won:
        player.coins += amount
        await context.respond(
            ":chart_with_upwards_trend: Повезло тебе сука <:Clueless:1126355741528297535>\n"
            f"Теперь у тебя {player.coins} <:chlenocoin:1129537623480881295>"
        )
    else:
        player.coins -= amount
        await context.respond(
            ":chart_with_downwards_trend: Лох хуле <:LUL:1128416818529321061>\n "
            f"Теперь у тебя {player.coins} <:chlenocoin:1129537623480881295>")

    player.bets += 1
    player.save()


@bot.command()
@discord.option(
    name="player",
    type=discord.Member,
    required=False,
)
async def stats(context: discord.ApplicationContext, player: discord.Member | None):
    if player is None:
        player_: Player = Player.get_or_none(Player.name == context.author.name)
    else:
        player_: Player = Player.get_or_none(Player.name == player.name)
    if player_ is None:
        return await ask_to_create_account(context)

    await context.respond(
        f":identification_card: Стата **{player_.name}**:\n"
        f"• **Деньги**: {player_.coins} <:chlenocoin:1129537623480881295>\n"
        f"• **Уровень**: {player_.level}\n"
        f"• **З/п**: {LEVELS_TO_RATES[player_.level]}"
    )


@bot.command()
@discord.option(
    name="amount",
    type=int,
    required=True,
)
@discord.option(
    name="recipient",
    type=discord.Member,
    required=True,
)
async def send(context: discord.ApplicationContext, amount: int, recipient: discord.Member):
    authorized = check_auth(context.author.name)
    if not authorized:
        return await ask_to_create_account(context)

    sender_account: Player = Player.get_or_none(Player.name == context.author.name)
    recipient_account: Player = Player.get_or_none(Player.name == recipient.name)
    if recipient_account is None:
        return await context.respond(f":red_square: Я не знаю кто такой {recipient.mention} <:Concerned:1126355619562131487>")

    if amount <= 0:
        return await context.respond(":red_square: Ты долбоёб? <:chel:1124482608420622416>")

    if sender_account.coins < amount:
        return await context.respond(":red_square: У тебя нет таких денег <:Concerned:1126355619562131487>")

    sender_account.coins -= amount
    recipient_account.coins += amount
    sender_account.save()
    recipient_account.save()

    await context.respond(f":incoming_envelope: Ты отправил {amount} <:chlenocoin:1129537623480881295> {recipient.mention}")


def main() -> None:
    schedule.every().hour.at(":00").do(reset_cooldowns)
    schedule.every().hour.at(":30").do(reset_cooldowns)
    threading.Thread(target=scheduling_tick, daemon=True).start()
    reset_cooldowns()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
