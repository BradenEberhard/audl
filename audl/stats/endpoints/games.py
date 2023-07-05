from audl.stats.endpoints._base import Endpoint
import requests
import pandas as pd

class Games(Endpoint):
    def __init__(self):
        super().__init__("https://www.backend.audlstats.com/api/v1/games")

    def get_request(self, endpoint):
        self.current_request = requests.get(f'{self.base_url}{endpoint}').json()['data']
    
    def set_games(self, years='all'):
        self.current_request = requests.get(f'{self.base_url}?date={years}').json()
    
    def get_games(self, years='all'):
        return pd.DataFrame(requests.get(f'{self.base_url}?date={years}').json()['data'])