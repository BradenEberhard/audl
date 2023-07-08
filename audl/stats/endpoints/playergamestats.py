#!/usr/bin/env/python

import json
import math
import pandas as pd
import numpy as np
import requests

from audl.stats.endpoints._base import Endpoint
from audl.stats.endpoints.playerprofile import PlayerProfile

from audl.stats.library.game_event import GameEventSimple, GameEventLineup, GameEventReceiver
from audl.stats.static.utils import get_quarter, get_throw_type, get_throwing_distance

class PlayerGameStats(Endpoint):

    def __init__(self):
        super().__init__("https://www.backend.audlstats.com/api/v1/")

    def get_request_as_df(self, endpoint):
        return pd.DataFrame(requests.get(f'{self.base_url}{endpoint}').json()['data'])

    def get_game_from_id(self, gameID):
        return pd.DataFrame(requests.get(f'{self.base_url}playerGameStats?gameID={gameID}').json()['data'])

    def get_all_game_ids(self):
        endpoint = "games?date=2011:"
        ids = self.get_request_as_df(endpoint)['gameID'].values
        return ids

    def get_box_stats(self, dates='2023'):
        '''
        dates: An inclusive date range. The full format is YYYY-MM-DD:YYYY-MM-DD, but you can exclude months or days and it will infer them. Examples:
        2021-06:2021-07 => All games during June or July
        2021 => All games during 2021
        2021-07-10: => All games on or after July 10th, 2021
        :2012-05 => All games during or before May, 2012

        default is all games in 2023
        dates='2011:' will get all games
        '''
        def split_player(row):
            return row['player']
        ids = self.get_request_as_df(f'games?date={dates}')['gameID'].values
        all_games = []
        for gameID in ids:
            game = self.get_request_as_df(f'playerGameStats?gameID={gameID}')
            game_info = self.get_request_as_df(f'games?gameIDs={gameID}')
            players = pd.json_normalize(game.apply(split_player, axis=1))
            box_stats = pd.merge(players, game.drop('player', axis=1), left_index=True, right_index=True)
            box_stats['gameID'] = gameID
            box_stats['date'] = game_info['startTimestamp'][0]
            all_games.append(box_stats)
        return pd.concat(all_games)