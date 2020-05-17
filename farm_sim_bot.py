import discord
from pynput.keyboard import Key, Controller
import time
import pyautogui
import auth
import boto3

keyboard = Controller()
client = discord.Client()
is_paused = False
pyautogui.FAILSAFE = False


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:  # prevent bot recursion
        return

    # User validation
    msg = message.content
    if msg.startswith("!timescale ") or msg == "!fspause" or msg == "!players":
        if (
            str(message.author)[: len(str(message.author)) - 5]
            not in auth.APPROVED_USERS
        ):
            await message.channel.send(
                "You are not authorised to send commands to this bot."
            )
            return

    if msg.startswith("!timescale "):
        await handle_timescale(msg[11:], message)
    elif msg == "!fspause":
        await handle_pause(message)
    elif msg == "!players":
        await handle_players(message)
    elif msg == "$esc":
        if str(message.author)[: len(str(message.author)) - 5] != auth.ADMIN:
            await message.channel.send("Admin only command.")
            return
        keyboard.press(Key.esc)
        time.sleep(0.1)
        keyboard.release(Key.esc)
        await message.add_reaction("🚜")


async def handle_timescale(selected_timescale, message):
    # 1, 5, 15, 30, 60, 120
    await message.channel.trigger_typing()
    ts_map = {"1": 0, "5": 1, "15": 2, "30": 3, "60": 4, "120": 5}
    eight_spam = ts_map.get(selected_timescale)

    if eight_spam is None:
        await message.channel.send(
            "The timescale you typed is invalid. Valid timescales: 1, 5, 15, 30, 60, 120"
        )
        return
    if selected_timescale != "120":
        for _ in range(5):
            keyboard.press("7")
            time.sleep(0.1)
            keyboard.release("7")
            time.sleep(0.1)
    for _ in range(eight_spam):
        keyboard.press("8")
        time.sleep(0.1)
        keyboard.release("8")
        time.sleep(0.1)
    await message.channel.send("Timescale set to " + selected_timescale + " 🚜")


async def handle_pause(message):
    global is_paused
    await message.channel.trigger_typing()
    if is_paused:
        is_paused = False
        keyboard.press(".")
        time.sleep(0.1)
        keyboard.release(".")
        await message.channel.send("Game is now unpaused.")
    elif not is_paused:
        is_paused = True
        keyboard.press(".")
        time.sleep(0.1)
        keyboard.release(".")
        await message.channel.send("Game is now paused.")


async def handle_players(message):
    try:
        await message.channel.trigger_typing()

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
        # await message.channel.send("", file=discord.File("player.png"))

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
            await message.channel.send(to_send)
        elif to_send == "Players:\n":
            await message.channel.send("Players: 0")
        # await message.channel.send("mouse at " + str(pyautogui.position()[0]) + " " + str(pyautogui.position()[1]))
    except Exception as e:
        await message.channel.send("Error. Something bad happened")
        with open("log.txt", "a") as f:
            f.write("\n" + str(e))


def main():
    client.run(auth.get_token())


if __name__ == "__main__":
    main()
