from collections import defaultdict
import pprint


def debug_print(obj):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(obj)


class Tile:
    def __init__(self, name, points, recurrence):
        self.name = name
        self.points = float(points)
        self.recurrence = recurrence


class KcTile:
    def __init__(self, name, points, recurrence, kc_required):
        self.name = name
        self.points = float(points)
        self.recurrence = recurrence
        self.kc_required = kc_required


class Team:
    def __init__(self, name):
        self.name = name
        self.members = {}
        self.points = 0
        self.channel = 0
        self.killcount = defaultdict(int)


class Player:
    def __init__(self, name, team):
        self.name = name
        self.points_gained = 0.0
        self.gp_gained = 0
        self.team = team
        self.deaths = 0
        self.killcount = defaultdict(int)

    def __str__(self):
        return self.name

class Bingo:
    def __init__(self):
        self.teams = {}
        self.players = {}
        self.game_tiles = {}
        self.tile_completions = defaultdict(int)

    def __str__(self):
        output = "Teams\n"
        for team in self.teams.values():
            player_info = [
                f"\t\t{player.name} ({player.points_gained} points and {player.gp_gained} gold). This player has died {player.deaths} times\n"
                for player in team.members.values()]
            player_names = "".join(player_info)
            output += f"\t{team.name} ({team.points} points):\n{player_names}\n"

        output += "\nTiles\n"
        for tile in self.game_tiles.values():
            output += f"\t{tile.name}: Worth {tile.points} points {tile.recurrence} times\n"

        return output

    def add_death(self, player_name):
        self.players[player_name].deaths = self.players[player_name].deaths + 1

    def get_player(self, player_name):
        return self.players[player_name]

    def add_value(self, player_name, value):
        player = self.get_player(player_name)
        player.gp_gained = player.gp_gained + value

    def set_team_channel(self, team_name, channelID):
        self.teams[team_name].channel = channelID

    def find_team_by_player(self, player_name):
        return self.players[player_name].team

    def new_team(self, name):
        self.teams[name] = Team(name)

    def rename_team(self, old_name, new_name):
        team = self.teams[old_name]
        team.name = new_name
        self.teams[new_name] = team
        del self.teams[old_name]

    def delete_team(self, name):
        del self.teams[name]

    def add_team_member(self, team_name, player_name):
        team = self.teams[team_name]
        player = Player(player_name, team)
        team.members[player_name] = player
        self.players[player_name] = player

    def remove_team_member(self, team_name, player_name):
        del self.teams[team_name].members[player_name]
        del self.players[player_name]

    def add_tile(self, name, points, recurrence):
        self.game_tiles[name] = Tile(name, points, recurrence)

    def award_tile(self, tile_name, team_name, player_name):
        tile = self.game_tiles[tile_name]
        team = self.teams[team_name]
        player = self.players[player_name]

        if self.tile_completions[(team, tile)] < int(tile.recurrence):
            team.points = team.points + int(tile.points)
            self.tile_completions[(team, tile)] = self.tile_completions[(team, tile)] + 1

            self.game_tiles[tile_name] = tile
            self.teams[team_name] = team
            self.players[player_name] = player

            return True

        return False

    def delete_tile(self, tile_name):
        del self.game_tiles[tile_name]

    def get_tile(self, tile_name):
        try:
            for key, value in self.game_tiles.items():
                if tile_name in key:
                    return value
            return None
        except:
            return None

    def is_tile(self, tile_name):
        try:
            for key in self.game_tiles.keys():
                if tile_name in key:
                    return True
            return False
        except:
            return False

    def add_kctile(self, tile_name, point_value, recurrence, kc_required):
        self.game_tiles[tile_name] = KcTile(tile_name, point_value, recurrence, kc_required)
