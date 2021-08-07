#!/usr/bin/env/python

import json
import pandas as pd
import numpy as np
import requests

from audl.stats.endpoints._base import Endpoint
from audl.stats.static import players
from audl.stats.library.parameters import TeamStatsName
from audl.stats.library.parameters import team_stats_perc_columns_names, team_stats_row_names


class GameStats(Endpoint):

    def __init__(self, game_id: str):
        self.game_id = game_id
        super().__init__("https://audl-stat-server.herokuapp.com/stats-pages/game/")
        self.endpoint = game_id
        self.url = self._get_url()
        self.json = self._get_json_from_url()

    def _get_json_from_url(self):
        return requests.get(self.url).json()

    def _get_game_metadata(self):
        game = self.json['game']
        team_season_home = game['team_season_home']
        team_season_away = game['team_season_away']
        score_home = game['score_home']
        score_away = game['score_away']
        score_times_home = game['score_times_home'][1:]
        score_times_away = game['score_times_away'][1:]
        pass

    def _get_teams_full_name(self):
        game = self.json['game']
        team_season_home = game['team_season_home']
        team_season_away = game['team_season_away']
        home_name = team_season_home['team']['name']
        home_city = team_season_home['city']
        home_full_name = f"{home_city} {home_name}"
        away_name = team_season_away['team']['name']
        away_city = team_season_away['city']
        away_full_name = f"{away_city} {away_name}"
        return home_full_name, away_full_name

    def _get_roster_df(self, roster):
        # get data from json
        rows = []
        for index, player in enumerate(roster):
            players = roster[index]
            identification_num = player['id']
            jersey_number = player['jersey_number']
            first_name = player['player']['first_name']
            last_name = player['player']['last_name']
            #  full_name = f"{first_name} {last_name}"
            player_id = player['player']['ext_player_id']
            row = [identification_num, first_name,
                   last_name, jersey_number, player_id]
            rows.append(row)

        # create data frame
        df = pd.DataFrame(rows)
        return df

    def _get_roster_home_team_df(self):
        home_roaster = self.json['rostersHome']
        return self._get_roster_df(home_roaster)

    def _get_roster_away_team_df(self):
        away_roaster = self.json['rostersAway']
        return self._get_roster_df(away_roaster)

    @staticmethod
    def _round_2_decimals(perc: float) -> float:
        return round(perc, 2)

    def _get_team_stats_blocks_turnovers(self, tsg: list) -> [int, int]:
        blocks = tsg['blocks']
        turnovers = tsg['turnovers']
        start_on_offense = tsg['startOnOffense']
        return blocks, turnovers

    def _get_team_stats_df_perc_from_json(self, tsg: list) -> list:
        # get stats from json
        completions_numerator = tsg['completionsNumer']
        completions_denominator = tsg['completionsDenom']
        d_lines_breaks_numerator = tsg['dLineBreaksNumer']
        d_lines_breaks_denominator = tsg['dLineBreaksDenom']
        hucks_numerator = tsg['hucksNumer']
        hucks_denominator = tsg['hucksDenom']
        o_line_holds_numerator = tsg['oLineHoldsNumer']
        o_line_holds_denominator = tsg['oLineHoldsDenom']
        red_zone_numerator = tsg['redZoneNumer']
        red_zone_denominator = tsg['redZoneDenom']

        # calculate percentage
        completion_perc = GameStats._round_2_decimals(
            completions_numerator / completions_denominator)
        hucks_perc = GameStats._round_2_decimals(
            hucks_numerator / hucks_denominator)
        offensive_holds_perc = GameStats._round_2_decimals(
            o_line_holds_numerator / o_line_holds_denominator)
        defensive_breaks_perc = GameStats._round_2_decimals(
            d_lines_breaks_numerator / d_lines_breaks_denominator)
        red_zone_perc = GameStats._round_2_decimals(
            red_zone_numerator / red_zone_denominator)

        # create dataframe
        data = [
            [TeamStatsName.Completions,
                completions_numerator, completions_denominator, completion_perc],
            [TeamStatsName.Hucks,
                hucks_numerator, hucks_denominator, hucks_perc],
            [TeamStatsName.Offensive_holds,
                o_line_holds_numerator, o_line_holds_denominator, offensive_holds_perc],
            [TeamStatsName.Defensive_breaks,
                d_lines_breaks_numerator, d_lines_breaks_denominator, defensive_breaks_perc],
            [TeamStatsName.Red_zone_possessions,
                red_zone_numerator, red_zone_denominator, red_zone_perc],
        ]
        df_perc = pd.DataFrame(data, columns=team_stats_perc_columns_names)
        return df_perc

    @staticmethod
    def _format_perc_to_string(perc: float) -> str:
        return "{:.0%}".format(perc)

    def _get_team_stats_col_formatted(self, tsg: list) -> list:
        # get percentage df and reformat into single column
        df_perc = self._get_team_stats_df_perc_from_json(tsg)
        df_perc['Percentage'] = df_perc['Percentage'].apply(
            GameStats._format_perc_to_string)
        df_perc['Concat'] = df_perc['Percentage'].map(
            str) + '(' + df_perc['Successful'].map(str) + '/' + df_perc['Opportunities'].map(str) + ')'

        # get blocks and turnovers count
        blocks, turnovers = self._get_team_stats_blocks_turnovers(tsg)
        column = list(df_perc['Concat'])
        column.append(blocks)
        column.append(turnovers)
        return column

    def _get_home_team_stats_formatted(self) -> list:
        tsgHome = self.json['tsgHome']
        df = self._get_team_stats_col_formatted(tsgHome)
        #  df = self._get_team_stats_df_perc_from_json(tsgHome)
        return df

    def _get_away_team_stats_formatted(self) -> list:
        tsgAway = self.json['tsgAway']
        df = self._get_team_stats_col_formatted(tsgAway)
        #  df = self._get_team_stats_df_perc_from_json(tsgAway)
        return df

    def _get_home_team_events(self):
        tsgHome = self.json['tsgHome']
        events = tsgHome['events']
        print(events)

    def get_box_scores(self):
        pass

    def get_team_stats(self) -> list:  # same format as audl
        # get column stats for each team
        home_team, away_team = self._get_teams_full_name()
        home_col_formatted = self._get_home_team_stats_formatted()
        away_col_formatted = self._get_away_team_stats_formatted()

        # combine columns into dataframe
        data = [team_stats_row_names,
                away_col_formatted, home_col_formatted]
        data_transposed = GameStats._transpose_list(data)
        header = ['', away_team, home_team]
        df = pd.DataFrame(data_transposed, columns=header)
        return df

    @staticmethod
    def _transpose_list(data: list) -> list:
        return np.array(data).T.tolist()

    def _get_player_stats_both_teams(self):
        pass

    def get_player_stats_home_team(self):
        pass

    def get_player_stats_away_team(self):
        pass

    def _get_play_by_play_lineups(self):
        pass
