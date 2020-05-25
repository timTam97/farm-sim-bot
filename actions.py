from pynput.keyboard import Key, Controller
import time
import pyautogui
import auth
import boto3
import datetime

is_paused = False
keyboard = Controller()


async def validate_user(ctx):
    msg = ctx.invoked_with
    if (
        msg in ["fspause", "timescale", "players", "esc"]
        and ctx.author.display_name not in auth.APPROVED_USERS
    ):
        await ctx.send("You are not authorised to send commands to this bot.")
        return False
    return True


async def handle_timescale(ctx, scale):
    # 1, 5, 15, 30, 60, 120
    await ctx.trigger_typing()
    ts_map = {"1": 0, "5": 1, "15": 2, "30": 3, "60": 4, "120": 5}
    key_press = ts_map.get(scale)

    if key_press is None:
        await ctx.send(
            "The timescale you typed is invalid. Valid timescales: 1, 5, 15, 30, 60, 120"
        )
        return
    if scale != "120":
        for _ in range(5):
            keyboard.press("7")
            time.sleep(0.1)
            keyboard.release("7")
            time.sleep(0.1)
    for _ in range(key_press):
        keyboard.press("8")
        time.sleep(0.1)
        keyboard.release("8")
        time.sleep(0.1)
    await ctx.send("Timescale set to " + scale + " 🚜")


async def handle_pause(ctx):
    global is_paused
    await ctx.trigger_typing()
    if is_paused:
        is_paused = False
        keyboard.press(".")
        time.sleep(0.1)
        keyboard.release(".")
        await ctx.send("Game is now unpaused.")
    elif not is_paused:
        is_paused = True
        keyboard.press(".")
        time.sleep(0.1)
        keyboard.release(".")
        await ctx.send("Game is now paused.")


async def handle_players(ctx):
    try:
        await ctx.trigger_typing()

        # Grab screenshot
        keyboard.press(Key.esc)
        time.sleep(0.1)
        keyboard.release(Key.esc)
        time.sleep(0.25)
        pyautogui.moveTo(x=506, y=28)
        pyautogui.click()
        time.sleep(0.25)
        pyautogui.screenshot("player.png", region=(93, 420, 259, 130))
        keyboard.press(Key.esc)
        time.sleep(0.1)
        keyboard.release(Key.esc)
        # await ctx.send("", file=discord.File("player.png"))

        # AWS magic
        to_send = ""
        aws_client = boto3.client("rekognition")
        with open("player.png", "rb") as image:
            response = aws_client.detect_text(Image={"Bytes": image.read()})
        for texts in response.get("TextDetections"):
            if texts.get("Type") == "LINE":
                to_send += texts["DetectedText"]
                to_send += "\n"

        # Nicer 0 player messages
        if to_send != "Players:\n":
            await ctx.send(to_send)
        elif to_send == "Players:\n":
            await ctx.send("Players: 0")
        # await ctx.send("mouse at " + str(pyautogui.position()[0]) + " " + str(pyautogui.position()[1]))
    except Exception as e:
        await ctx.send("Error. Something bad happened")
        await write_log(e)


async def handle_esc(ctx):
    if ctx.author.display_name != auth.ADMIN:
        await ctx.send("Admin only command.")
        return
    keyboard.press(Key.esc)
    time.sleep(0.1)
    keyboard.release(Key.esc)
    await ctx.message.add_reaction("🚜")


async def write_log(event):
    with open("run.log", "a") as f:
        to_write = "[" + str(datetime.datetime.today())[:-7] + "] "
        to_write += str(event) + "\n"
        f.write(to_write)