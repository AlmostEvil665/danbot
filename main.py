from discord import Intents, Client, Message
import re

"""
Wishlist

Least Lucky
Most XP
Most Deaths
Total gp earned by clan (done)

"""


from bingo import *
from responses import get_response

TOKEN = 'MTIxNjI0ODkzNjczODU5MDc1MA.GIOK7i.nCir_rKClu7r5MG31bDOU9IIL-xQssjlRSMSic'
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
    if channel: await(channel.send(content))
    else: print("Channel not found")

@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')


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

        player = message.embeds[0].description.lower().split('\n')[0]

        dropdata = message.embeds[0].description.lower().split('\n')[1:]
        for drop in dropdata:
            dropname, value = extract_data_from_string(drop)
            value = value.lower().replace('k', "000")
            bingo.add_value(player, int(value))
            if bingo.is_tile(dropname.lower()):
                team = bingo.find_team_by_player(player)
                if bingo.award_tile(dropname.lower(), team.name, player.lower()):
                    await send_channel(team.channel, player + " got a " + dropname + " and " + team.name + " has been awarded " + str(bingo.get_tile(dropname).points) + " points!")
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
                                        "!addteam Team Name - Adds a new team to the bingo\n"
                                        "!deleteteam Team Name - Deletes a team from the bingo\n"
                                        "!renameteam Old Name, New Name - Renames a bingo team\n"
                                        "!setteamchannel Team Name, Channel ID\n"
                                        "\n"
                                        "__**PLAYERS**__\n"
                                        "If a player name changes during bingo just !addplayer with their new name to "
                                        "the team and delete their old name\n"
                                        "!addplayer Team Name, Player Name - Adds a player to a given team\n"
                                        "!removeplayer Team Name, Player Name - Removes a player from a given team\n"
                                        "\n"
                                        "__**TILES**__\n"
                                        "All tiles **must be named as their drop**. Eg: Elidinis Ward must be ("
                                        "!addtile Elidinis' Ward 1)\n"
                                        "!addtile Exact Item Name, Point Value, Recurrence - Recurrence means how "
                                        "many times the tile can be repeated. If recurrence is not included we assume "
                                        "a recurrence of 1\n"
                                        "!deletetile Exact Item Name - Deletes the tile\n"
                                        "!awardtile Tile Name, Team Name, Player Name - Awards a team a tile if the "
                                        "bot misses it\n")

        # Bingo
        if content.startswith("!newbingo"):
            bingo = Bingo()
            await send_message(message, "Bingo created! All previous bingo data is now gone")

        if content.startswith("!dbg"):
            await send_message(message, str(bingo))

        # Teams
        if content.startswith("!addteam"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                bingo.new_team(parameters[0])
                await send_message(message, "Team " + parameters[0] + " added!")
                return
            except Exception as e:
                await send_message(message, e.__str__())

        if content.startswith("!deleteteam"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                bingo.delete_team(parameters[0])
                await send_message(message, "deleted team :(")
                return
            except:
                await send_message(message, "Incorrect command usage. !deleteteam Team Name")

        if content.startswith("!renameteam"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                bingo.rename_team(parameters[0], parameters[1])
                await send_message(message, "Renamed team!")
            except:
                await send_message(message, "Incorrect command usage. !renameteam Oldname, Newname")

        if content.startswith("!setteamchannel"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                bingo.set_team_channel(parameters[0], parameters[1])
                await send_channel(bingo.teams[parameters[0]].channel, "Welcome to the bingo!")
            except Exception as e:
                await send_message(message, e.__str__())

        # Players

        if content.startswith("!addplayer"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                bingo.add_team_member(parameters[0], parameters[1])
                await send_message(message, "Added " + parameters[1] + " to team " + parameters[0] + "!")
            except Exception as e:
                await send_message(message, e.__str__())

        if content.startswith("!removeplayer"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                bingo.remove_team_member(parameters[0], parameters[1])
                await send_message(message, "Removed " + parameters[1] + " from team " + parameters[0] + "!")
            except Exception as e:
                await send_message(message, e.__str__())

        # Tiles

        if content.startswith("!addtile"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                if len(parameters) == 2:
                    bingo.add_tile(parameters[0], parameters[1], 1)
                else:
                    bingo.add_tile(parameters[0], parameters[1], parameters[2])
                await send_message(message, "Tile added!")
            except Exception as e:
                await send_message(message, e.__str__())

        if content.startswith("!deletetile"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                bingo.delete_tile(parameters[0])
                await send_message(message, "Tile deleted!")
            except Exception as e:
                await send_message(message, e.__str__())

        if content.startswith("!awardtile"):
            try:
                parameters = content[content.find(' ') + 1:].split(', ')
                bingo.award_tile(parameters[0], parameters[1], parameters[2])
                await send_message(message, "Tile awarded!")
            except Exception as e:
                await send_message(message, e.__str__())
# STEP 5: MAIN ENTRY POINT
def main() -> None:
    bingo = Bingo()
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
