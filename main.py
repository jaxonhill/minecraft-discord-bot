import os
from dotenv import load_dotenv, find_dotenv
import discord
from discord import app_commands
from discord.ext import commands

# Get the secret token for the bot
load_dotenv(find_dotenv())
TOKEN = os.getenv("TOKEN")

# Create intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot with commands
bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    print("Bot is up!")
    # Sync all the commands that we have to "/" commands when the bot starts up
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as err:
        print(err)


@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hey {interaction.user.mention}! This is a slash command"
    )


@bot.tree.command(name="say")
@app_commands.describe(arg="What should I say?")
async def say(interaction: discord.Interaction, arg: str):
    await interaction.response.send_message(f"{interaction.user.name} said `{arg}`")


@bot.tree.command(name="create_location")
@app_commands.describe(location_name="name:", x_coord="X:", y_coord="Y:", z_coord="Z:")
async def set_coords(
    interaction: discord.Interaction,
    location_name: str,
    x_coord: str,
    y_coord: str,
    z_coord: str,
):
    # Ensure they entered valid string entry for location
    # TODO: When you have database, ensure that the location they are entering does not already
    # exist in their list of places. If it does, then explain this to them with await interaction...

    # Ensure they entered valid integers for coordinates
    try:
        x_coord = int(x_coord)
        y_coord = int(y_coord)
        z_coord = int(z_coord)
    except ValueError:
        # They did not pass in integers
        await interaction.response.send_message(
            "Something went wrong. Please enter only whole numbers with no spaces or decimal points."
        )

        # Retrun to exit out of this and not execute rest of code
        return

    # If here, the inputs are valid
    await interaction.response.send_message(
        f"You created the location `{location_name}` with the coordinates \
    X: `{x_coord}` Y: `{y_coord}` Z: `{z_coord}`"
    )


bot.run(TOKEN)


# class MyClient(discord.Client):
#     async def on_ready(self):
#         print(f"Logged on as {self.user}")

#     async def on_message(self, message):
#         # If the message is from the bot itself, do not do anything
#         if message.author == self.user:
#             return

#         user_message = ""

#         # Check that they used the command prefix
#         if message.content[0] == "?":
#             # Then set the user's command to the
#             user_command = message.content[1:]
#         else:
#             return

#         print(f"Message from {message.author}: {message.content}")


# # Get the secret token for the bot
# load_dotenv(find_dotenv())
# TOKEN = os.getenv("TOKEN")
# print(TOKEN)

# # Create intents and create the instance of the bot
# intents = discord.Intents.default()
# intents.message_content = True
# client = MyClient(intents=intents)

# client.run(TOKEN)
