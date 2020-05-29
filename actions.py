import time
import pyautogui
import auth
import boto3
import datetime

is_paused = False
pyautogui.FAILSAFE = False


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
        pyautogui.press("7", presses=5, interval=0.2)
    pyautogui.press("8", presses=key_press, interval=0.2)
    await ctx.send("Timescale set to " + scale + " 🚜")


async def handle_pause(ctx):
    global is_paused
    await ctx.trigger_typing()
    if is_paused:
        is_paused = False
        pyautogui.press(".")
        await ctx.send("Game is now unpaused.")
    elif not is_paused:
        is_paused = True
        pyautogui.press(".")
        await ctx.send("Game is now paused.")


async def handle_players(ctx):
    await ctx.trigger_typing()

    # Grab screenshot
    pyautogui.press("esc")
    time.sleep(0.25)
    pyautogui.click(x=506, y=28)
    time.sleep(0.25)
    pyautogui.screenshot("player.png", region=(93, 420, 259, 130))
    pyautogui.press("esc")

    try:
        # AWS magic
        player_text = "Players:\n"  # grab_text("player.png")
        if player_text == "Players:\n":  # Nicer 0 player messages
            await ctx.send("Players: 0")
            return
        await ctx.send(player_text)
    except Exception as e:
        await ctx.send("Error. Something bad happened")
        await write_log(e)


def grab_text(file_name):
    to_send = ""
    aws_client = boto3.client("rekognition")
    with open(file_name, "rb") as image:
        response = aws_client.detect_text(Image={"Bytes": image.read()})
    for texts in response.get("TextDetections"):
        if texts.get("Type") == "LINE":
            to_send += texts["DetectedText"]
            to_send += "\n"
    return to_send


async def handle_esc(ctx):
    if ctx.author.display_name != auth.ADMIN:
        await ctx.send("Admin only command.")
        return
    pyautogui.press("esc")
    await ctx.message.add_reaction("🚜")


async def write_log(event):
    with open("run.log", "a") as f:
        to_write = "[" + str(datetime.datetime.today())[:-7] + "] "
        to_write += str(event) + "\n"
        f.write(to_write)
