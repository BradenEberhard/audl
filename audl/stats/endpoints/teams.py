from audl.stats.endpoints._base import Endpoint
import requests
import pandas as pd

class Teams(Endpoint):
    def __init__(self):
        super().__init__("https://www.backend.audlstats.com/api/v1/teams")

    def get_request(self, endpoint):
        self.current_request = requests.get(f'{self.base_url}{endpoint}').json()['data']
    
    def set_teams(self, years='2021:'):
        self.current_request = requests.get(f'{self.base_url}?data={years}').json()
    
    def get_teams(self, years='2021:'):
        return pd.DataFrame(requests.get(f'{self.base_url}?data={years}').json()['data'])

