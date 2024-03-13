import json

from discord import Intents, Client, Message
import re

"""
Wishlist

Least Lucky
Most XP
Most Deaths
Total gp earned by clan (done)
Multiline commands for toortle brain
Useful error logging
"""

from bingo import *
from responses import get_response

with open('config.json') as f:
    config = json.load(f)

TOKEN = config.get('TOKEN')
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.all()
client: Client = Client(intents=intents)

global bingo
bingo = Bingo()


async def send_message(message: Message, content: str) -> None:
    channel = message.channel
    await channel.send(content)


async def send_channel(CHANNEL_ID, content: str) -> None:
    channel = client.get_channel(int(CHANNEL_ID))
    if channel:
        await(channel.send(content))
    else:
        print("Channel not found")


@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')


async def get_input() -> str:
    msg = await client.wait_for('message', timeout=60.0)
    if msg.author.bot:
        msg = await client.wait_for('message', timeout=60)

    return msg.content


def extract_data_from_string(text):
    # Find the index of the first '[' and ']'
    start_index_name = text.find('[')
    end_index_name = text.find(']')

    # Extract the name between '[' and ']'
    name = text[start_index_name + 1:end_index_name]

    # Find the index of the first '(' and ')'
    start_index_value = text.find('(')
    end_index_value = text.find(')')

    # Find the index of the next '(' and ')' to get the start and end positions of the second pair
    start_index_next = text.find('(', end_index_value)
    end_index_next = text.find(')', start_index_next)

    # Extract the value between '(' and ')'
    value = text[start_index_next + 1:end_index_next]

    return name, value


# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    global bingo
    # Captain Hook
    if message.author.bot and message.author.name == "Captain Hook":
        print(f"{message.embeds[0].description}")

        player = message.embeds[0].description.lower().split('\n')[1]
        dropdata = message.embeds[0].description.lower().split('\n')[2:]
        for drop in dropdata:
            dropname, value = extract_data_from_string(drop)
            value = value.lower().replace('k', "000")
            bingo.add_value(player, int(value))
            if bingo.is_tile(dropname.lower()):
                team = bingo.find_team_by_player(player)
                if bingo.award_tile(dropname.lower(), team.name, player.lower()):
                    await send_channel(team.channel,
                                       player + " got a " + dropname + " and " + team.name + " has been awarded " + str(
                                           bingo.get_tile(dropname).points) + " points!")
        return

    """
    Default command
    
            if content.startswith("!"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
            except Exception as e:
                await send_message(message, e.__str__())
    
    """

    content = message.content.lower()
    if content.startswith('!'):
        if content.startswith("!help"):
            await send_message(message, ""
                                        "__**HELP**__\n"
                                        "Start every new bingo with !newbingo. This wipes the previous bingo data so "
                                        "we can make a new board and teams\n"
                                        "\n"
                                        "__**TEAMS**__\n"
                                        "!addteam - Adds a new team to the bingo\n"
                                        "!deleteteam - Deletes a team from the bingo\n"
                                        "!renameteam - Renames a bingo team\n"
                                        "!setteamchannel - Sets a chat channel to report team point gains\n"
                                        "\n"
                                        "__**PLAYERS**__\n"
                                        "If a player name changes during bingo just !addplayer with their new name to "
                                        "the team and delete their old name\n"
                                        "!addplayer - Adds a player to a given team\n"
                                        "!removeplayer - Removes a player from a given team\n"
                                        "\n"
                                        "__**TILES**__\n"
                                        "All tiles **must be named as their drop**. Eg: Elidinis Ward must be "
                                        "\"Elidinis' Ward\"\n"
                                        "!addtile - Add a tile to the bingo\n"
                                        "!deletetile - Deletes a tile\n"
                                        "!awardtile - Awards a team a tile if the bot misses it\n")

        # Bingo
        if content.startswith("!newbingo"):
            bingo = Bingo()
            await send_message(message, "Bingo created! All previous bingo data is now gone")

        if content.startswith("!dbg"):
            await send_message(message, str(bingo))

        # Teams
        if content.startswith("!addteam"):
            try:
                await send_message(message, "What is the team name?")
                team_name = await get_input()
                bingo.new_team(team_name)
                await send_message(message, f"Team {team_name} added!")
                return
            except Exception as e:
                await send_message(message, e.__str__())

        if content.startswith("!deleteteam"):
            try:
                await send_message(message, "What is the team name?")
                team_name = await get_input()
                bingo.delete_team(team_name)
                await send_message(message, f"Team {team_name} deleted :(")
                return
            except:
                await send_message(message, "Incorrect command usage. !deleteteam Team Name")

        if content.startswith("!renameteam"):
            try:
                await send_message(message, "What is the team you would like to rename?")
                old_team_name = await get_input()
                await send_message(message, "What would you like to rename the team to?")
                new_team_name = await get_input()
                bingo.rename_team(old_team_name, new_team_name)
                await send_message(message, f"Team {old_team_name} has been updated to {new_team_name}")
                return
            except:
                await send_message(message, "I shit the bed. UwU")

        if content.startswith("!setteamchannel"):
            try:
                await send_message(message, "What team would you like to set the chat channel for?")
                team_name = await get_input()
                await send_message(message, "Right click on the chat channel and click \"Copy Channel ID\" and paste "
                                            "it into the chat.")
                channel_id = await get_input()
                bingo.set_team_channel(team_name, channel_id)
                await send_message(message, "Channel set! Check the chat channel and make sure I introduced myself")
                await send_channel(channel_id, "Welcome to the bingo!")
            except Exception as e:
                await send_message(message, e.__str__())

        # Players

        if content.startswith("!addplayer"):
            try:
                await send_message(message, "What is the players name?")
                player_name = await get_input()
                await send_message(message, "What team is this player on?")
                team_name = await get_input()
                bingo.add_team_member(team_name, player_name)
                await send_message(message, f"Player {player_name} added to team {team_name}!")
            except Exception as e:
                await send_message(message, e.__str__())

        if content.startswith("!removeplayer"):
            try:
                await send_message(message, "What is the players name?")
                player_name = await get_input()
                await send_message(message, "What team is this player on?")
                team_name = await get_input()
                bingo.remove_team_member(player_name, team_name)
                await send_message(message, f"Player {player_name} has been removed from team {team_name} :(")
            except Exception as e:
                await send_message(message, e.__str__())

        # Tiles

        if content.startswith("!addtile"):
            try:
                await send_message(message, "What are the possible drops for this tile? (Separate them by \"/\")")
                tile_name = await get_input()
                await send_message(message, "How many points is this tile worth?")
                point_value = await get_input()
                await send_message(message, "How many times can this tile be completed?")
                recurrence = await get_input()
                bingo.add_tile(tile_name, point_value, recurrence)
                await send_message(message,
                                   f"Tile {tile_name} has been added for {point_value} points and can be repeated {recurrence} time(s)")
            except Exception as e:
                await send_message(message, e.__str__())

        if content.startswith("!deletetile"):
            try:
                await send_message(message,
                                   "What are the possible drops for the tile you would like to delete? (Separate them by \"/\")")
                tile_name = await get_input()
                bingo.delete_tile(tile_name)
                await send_message(message, f"Tile {tile_name} has been deleted")
            except Exception as e:
                await send_message(message, e.__str__())

        if content.startswith("!awardtile"):
            try:
                await send_message(message,
                                   "What are the possible drops for the tile you would like to award? (Separate them by \"/\")")
                tile_name = await get_input()
                await send_message(message, "What team is being awarded this tile?")
                team_name = await get_input()
                await send_message(message, 'Which player completed this tile?')
                player_name = await get_input()
                bingo.award_tile(tile_name, team_name, player_name)
            except Exception as e:
                await send_message(message, e.__str__())


# STEP 5: MAIN ENTRY POINT
def main() -> None:
    bingo = Bingo()
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
