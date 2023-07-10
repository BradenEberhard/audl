from audl.stats.endpoints._base import Endpoint
import requests
import pandas as pd

class Games(Endpoint):
    def __init__(self):
        super().__init__("https://www.backend.audlstats.com/api/v1/games")

    def get_request(self, endpoint):
        self.current_request = requests.get(f'{self.base_url}{endpoint}').json()['data']
    
    def set_games(self, years='2021:'):
        self.current_request = requests.get(f'{self.base_url}?date={years}').json()
    
    def get_games(self, years='2021:'):
        return pd.DataFrame(requests.get(f'{self.base_url}?date={years}').json()['data'])
    
    def get_season_stats(self, season='2023'):
        stats = requests.get(f'https://www.backend.audlstats.com/web-api/team-stats?limit=50&year={season}').json()['stats']
        return stats