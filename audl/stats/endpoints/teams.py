from audl.stats.endpoints._base import Endpoint
import requests
import pandas as pd

class Teams(Endpoint):
    def __init__(self):
        super().__init__("https://www.backend.audlstats.com/api/v1/teams")

    def get_request(self, endpoint):
        self.current_request = requests.get(f'{self.base_url}{endpoint}').json()['data']
    
    def set_teams(self, years='all'):
        self.current_request = requests.get(f'{self.base_url}?years={years}').json()
    
    def get_teams(self, years='all'):
        return pd.DataFrame(requests.get(f'{self.base_url}?years={years}').json()['data'])

