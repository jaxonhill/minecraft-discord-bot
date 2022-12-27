import os
from dotenv import load_dotenv, find_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import pymongo
from pymongo import MongoClient

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


@bot.event
async def on_resumed():
    print("Bot resumed!")
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
    if num_documents >= 20:
        await interaction.response.send_message(
            "You have 20 locations. This is the max number. Delete one with the `/delete` command before adding another."
        )
        return

    # If here, all in puts/parameters are valid
    post_data = {"name": location_name, "x": x_coord, "y": y_coord, "z": z_coord}
    try:
        collection.insert_one(post_data)
    except Exception as error:  # Let the user know if there was an error adding to the database
        await interaction.response.send_message(
            f"Something went wrong when adding the data. The error is: `{error}`"
        )
        return

    await interaction.response.send_message(
        f"You created the location `{location_name}` with the coordinates :regional_indicator_x: `{x_coord}`   :regional_indicator_y: `{y_coord}`   :regional_indicator_z: `{z_coord}`"
    )


@bot.tree.command(name="list")
async def get_list(interaction: discord.Interaction):
    num_of_locations = collection.count_documents({})

    # If the number of locations is 0, then tell them they don't have any
    if num_of_locations <= 0:
        await interaction.response.send_message(
            "You don't have any locations! Add one with the `/create_location` command."
        )
        return

    # Otherwise start creating the Embed message
    embed = discord.Embed(
        title="Coordinates",
        color=discord.Color.blue(),
    )

    # Retrieve all the locations and add them as fields to the embed
    locations = collection.find({})

    for location in locations:
        embed.add_field(
            name=location["name"],
            value=f":regional_indicator_x: `{location['x']}`   :regional_indicator_y: `{location['y']}`   :regional_indicator_z: `{location['z']}`",
            inline=False,
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="get")
@app_commands.describe(new_location_name="location:")
async def get_location(interaction: discord.Interaction, new_location_name: str):
    # Lowercase new_location_name and strip leading and trailing spaces to compare it to database
    new_location_name.lower()
    new_location_name.strip()

    the_location = collection.find_one({"name": new_location_name})

    # Check if the location they entered matches one in the database
    if the_location == None:
        await interaction.response.send_message(
            f"Location: `{new_location_name}` does not exist. Check your spelling and check all locations with the `/list` command."
        )
        return

    # If it does exist, then execute rest of code
    embed = discord.Embed(
        title=the_location["name"],
        color=discord.Color.blue(),
    )

    embed.add_field(
        name="Coordinates",
        value=f":regional_indicator_x: `{the_location['x']}`   :regional_indicator_y: `{the_location['y']}`   :regional_indicator_z: `{the_location['z']}`",
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="delete")
@app_commands.describe(another_location_name="location:")
async def delete_location(interaction: discord.Interaction, another_location_name: str):
    # Lowercase another_location_name and strip leading and trailing spaces to compare it to database
    another_location_name.lower()
    another_location_name.strip()

    the_location = collection.find_one({"name": another_location_name})

    # Check if the location they entered matches one in the database
    if the_location == None:
        await interaction.response.send_message(
            f"Location: `{another_location_name}` does not exist. Check your spelling and check all locations with the `/list` command. Location names are case sensitive."
        )
        return

    # If it does exist, then delete it from the database
    collection.delete_one({"name": the_location["name"]})
    await interaction.response.send_message(
        f"Deleted the location: `{another_location_name}`"
    )


if __name__ == "__main__":
    bot.run(TOKEN)
