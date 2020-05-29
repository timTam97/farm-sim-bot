from discord.ext import commands
import actions
import auth

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))


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
    bot.run(auth.TOKEN)


if __name__ == "__main__":
    main()
