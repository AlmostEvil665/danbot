from collections import defaultdict
import pprint


def debug_print(obj):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(obj)


class Tile:
    def __init__(self, name, points, recurrence):
        self.name = name
        self.points = points
        self.recurrence = recurrence


class Team:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.points = 0
        self.channel = 0


class Player:
    def __init__(self, name):
        self.name = name
        self.points_gained = 0
        self.gp_gained = 0

    def __str__(self):
        return self.name


class Bingo:
    def __init__(self):
        self.teams = {}
        self.game_tiles = []
        self.tile_completions = defaultdict(int)

    def __str__(self):
        output = "Teams\n"
        for team in self.teams.values():
            player_info = [f"{player.name} ({player.points_gained} points and {player.gp_gained} gold)" for player in team.members]
            player_names = ", ".join(player_info)
            output += f"\t{team.name} ({team.points} points): {player_names}\n"

        output += "\nTiles\n"
        for tile in self.game_tiles:
            output += f"\t{tile.name}: Worth {tile.points} points {tile.recurrence} times\n"

        return output

    def get_player(self, player_name):
        for team in self.teams.values():
            for member in team.members:
                if member.name == player_name:
                    return member

    def add_value(self, player_name, value):
        player = self.get_player(player_name)
        player.gp_gained = player.gp_gained + value

    def print(self):
        print("Teams")
        for team in self.teams.values():
            player_names = ", ".join(player.name for player in team.members)
            print(f"\t{team.name} ({team.points} points): {player_names}")

        print()
        print("Tiles")
        for tile in self.game_tiles:
            print(f"\t{tile.name}: Worth {tile.points} points {tile.recurrence} times")

    def set_team_channel(self, team_name, channelID):
        self.teams[team_name].channel = channelID


    def find_team_by_player(self, player_name):
        for team in self.teams.values():
            for player in team.members:
                if player.name == player_name:
                    return team

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
        team.members.append(Player(player_name))

    def remove_team_member(self, team_name, player_name):
        team = self.teams[team_name]
        for player in team.members:
            if player.name == player_name:
                team.members.remove(player)

    def add_tile(self, name, points, recurrence):
        self.game_tiles.append(Tile(name, points, recurrence))

    def award_tile(self, tile_name, team_name, player_name):
        for tile in self.game_tiles:
            if tile.name == tile_name:
                team = self.teams[team_name]
                if self.tile_completions[(team, tile)] < int(tile.recurrence):
                    team.points = team.points + int(tile.points)
                    self.tile_completions[(team, tile)] = self.tile_completions[(team, tile)] + 1
                    for member in self.teams[team_name].members:
                        if member.name == player_name:
                            member.points_gained = member.points_gained + int(tile.points)
                            return True
                break

    def delete_tile(self, tile_name):
        for tile in self.game_tiles:
            if tile.name == tile_name:
                self.game_tiles.remove(tile)
                return

    def is_tile(self, dropname):
        for tile in self.game_tiles:
            if tile.name == dropname:
                return True
        return False

    def get_tile(self, dropname):
        for tile in self.game_tiles:
            if tile.name == dropname:
                return tile
