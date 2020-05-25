from discord.ext import commands
from pynput.keyboard import Key, Controller
import time
import pyautogui
import auth
import boto3
import actions

keyboard = Controller()
pyautogui.FAILSAFE = False
bot = commands.Bot(command_prefix="!")


@bot.command()
async def timescale(ctx, scale):
    if await actions.validate_user(ctx):
        await actions.handle_timescale(ctx, scale)


@bot.command()
async def fspause(ctx):
    if await actions.validate_user(ctx):
        await actions.handle_pause(ctx)


@bot.command()
async def players(ctx):
    if await actions.validate_user(ctx):
        await actions.handle_players(ctx)


@bot.command()
async def esc(ctx):
    await actions.handle_esc(ctx)


def main():
    bot.run(auth.get_token())


if __name__ == "__main__":
    main()
