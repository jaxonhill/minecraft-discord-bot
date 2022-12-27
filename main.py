import os
from dotenv import load_dotenv, find_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import time

test_json = [
    {
        "1260483": {
            "spawn": {
                "x": 15,
                "y": 64,
                "z": 125,
            },
            "skeleton spawner": {
                "x": 50,
                "y": 25,
                "z": 424,
            },
        }
    }
]

# Get the secret token for the bot
load_dotenv(find_dotenv())
TOKEN = os.getenv("TOKEN")

# Initialize connection to the MongoDB database
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
cluster = MongoClient(
    f"mongodb+srv://jaxon20:{MONGO_PASSWORD}@craftbot.vccx7r0.mongodb.net/?retryWrites=true&w=majority"
)
db = cluster["Craftbot"]
collection = db["locations"]

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


@bot.tree.command(name="create_location")
@app_commands.describe(location_name="name:", x_coord="x:", y_coord="y:", z_coord="z:")
async def set_coords(
    interaction: discord.Interaction,
    location_name: str,
    x_coord: str,
    y_coord: str,
    z_coord: str,
):

    # Remove leading and trailing spaces from all the parameters just in case the user added some
    location_name.strip()
    x_coord.strip()
    y_coord.strip()
    z_coord.strip()

    # Lower case location names to make them easier to sort and find
    location_name = location_name.lower()

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

    # Ensure that location does not already exist
    if collection.find_one({"name": location_name}) != None:
        await interaction.response.send_message(
            f"Location: `{location_name}` already exists. Check all locations with the `/list` command."
        )
        return

    # Ensure that there are not more than 20 locations as this is the max fields for embeds
    num_documents = collection.count_documents({})
    print(num_documents)
    if num_documents >= 20:
        await interaction.response.send_message(
            "You have 20 locations. This is the max number. Delete one with the `/delete` command before adding another."
        )
        return

    # If here, the inputs are valid
    await interaction.response.send_message(
        f"You created the location `{location_name}` with the coordinates :regional_indicator_x: `{x_coord}` :regional_indicator_y: `{y_coord}` :regional_indicator_z: `{z_coord}`"
    )


@bot.tree.command(name="list")
async def get_list(interaction: discord.Interaction):
    # TODO: Get the server ID right here
    # num_of_locations = collection.count_documents({})
    # print(num_of_locations)

    embed = discord.Embed(
        title="Coordinates",
        color=discord.Color.blue(),
    )

    embed.add_field(
        name="spawn",
        value=":regional_indicator_x: `25`   :regional_indicator_y: `73`   :regional_indicator_z: `2048`",
        inline=False,
    )
    embed.add_field(
        name="skeleton spawner",
        value=":regional_indicator_x: `4022`   :regional_indicator_y: `34`   :regional_indicator_z: `158`",
        inline=False,
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="get")
@app_commands.describe(location_name="location:")
async def get_location(interaction: discord.Interaction, location_name: str):
    # TODO: Check if the location they entered matches one in the database

    # if it does, then do the rest of this code
    embed = discord.Embed(
        title="skeleton spawner",
        color=discord.Color.blue(),
    )

    embed.add_field(
        name="Coordinates",
        value=":regional_indicator_x: `4022`   :regional_indicator_y: `34`   :regional_indicator_z: `158`",
    )

    await interaction.response.send_message(embed=embed)


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
