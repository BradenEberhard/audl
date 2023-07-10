#!/usr/bin/env/python

import pandas as pd
import requests
from audl.stats.endpoints._base import Endpoint

class GameEventsProxy(Endpoint):
    def __init__(self):
        super().__init__("https://www.backend.audlstats.com/api/v1/")

    def get_request(self, endpoint):
        self.current_request = requests.get(f'{self.base_url}{endpoint}').json()['data']

    def get_throws_from_id(self, gameID):
        self.get_request(f'gameEvents?gameID={gameID}')

        rows = []
        for event in self.current_request['homeEvents']:
            if event['type'] in [18, 19, 20, 22, 23]:
                turnover = 1 if event['type'] in [20, 22, 23] else 0
                event['turnover'] = turnover
                if 'receiverX' not in event:
                    event['receiverX'], event['receiverY'] = event['turnoverX'], event['turnoverY']
                event['is_home_team'], event['turnoverX'], event['turnoverY'] = True, None, None
                rows.append(event)

        for event in self.current_request['awayEvents']:
            if event['type'] in [18, 19, 20, 22, 23]:
                turnover = 1 if event['type'] in [20, 22, 23] else 0
                event['turnover'] = turnover
                if 'receiverX' not in event:
                    event['receiverX'], event['receiverY'] = event['turnoverX'], event['turnoverY']
                event['is_home_team'], event['turnoverX'], event['turnoverY'] = False, None, None
                rows.append(event)

        return pd.DataFrame(rows).drop(['turnoverX', 'turnoverY'], axis=1)


    def get_pulls_from_id(self, gameID):
        self.get_request(f'gameEvents?gameID={gameID}')
        rows = []
        for event in self.current_request['homeEvents']:
            pull_row = {}
            if event['type'] == 7:
                pull_row['pullX'] = event['pullX']
                pull_row['pullY'] = event['pullY']
                pull_row['pullMs'] = event['pullMs']
                pull_row['puller'] = event['puller']
                pull_row['in_bounds'] = True
                pull_row['is_home_team'] = True
                rows.append(pull_row)
            if event['type'] == 8:
                pull_row['pullX'] = None
                pull_row['pullY'] = None
                pull_row['pullMs'] = None
                pull_row['puller'] = event['puller']
                pull_row['in_bounds'] = False
                pull_row['is_home_team'] = True
                rows.append(pull_row)
                

        for event in self.current_request['awayEvents']:
            pull_row = {}
            if event['type'] == 7:
                pull_row['pullX'] = event['pullX']
                pull_row['pullY'] = event['pullY']
                pull_row['pullMs'] = event['pullMs']
                pull_row['puller'] = event['puller']
                pull_row['in_bounds'] = True
                pull_row['is_home_team'] = False
                rows.append(pull_row)
            if event['type'] == 8:
                pull_row['pullX'] = None
                pull_row['pullY'] = None
                pull_row['pullMs'] = None
                pull_row['puller'] = event['puller']
                pull_row['in_bounds'] = False
                pull_row['is_home_team'] = False
                rows.append(pull_row)

        return pd.DataFrame(rows)

    def get_penalties_from_id(self, gameID): #TODO check who is on offense, count both recording and opposing teams
        self.get_request(f'gameEvents?gameID={gameID}')
        home_penalties, away_penalties = 0, 0
        for event in self.current_request['homeEvents']:
            if event['type'] == 16:
                home_penalties = home_penalties + 1
                
        for event in self.current_request['awayEvents']:
            if event['type'] == 16:
                away_penalties = away_penalties + 1
        return home_penalties, away_penalties
    
    
class TeamEvents():
    class PullEvent():
        def __init__(self, puller = None, pull_x = None, pull_y = None, pull_ms = None):
            self.puller = puller
            self.pull_x = pull_x
            self.pull_y = pull_y
            self.pull_ms = pull_ms

    class ThrowEvent():
        def __init__(self, thrower, thrower_x, thrower_y, receiver, receiver_x, receiver_y, turnover):
            self.thrower = thrower
            self.thrower_x = thrower_x
            self.thrower_y = thrower_y
            self.receiver = receiver
            self.receiver_x = receiver_x
            self.receiver_y = receiver_y
            self.turnover = turnover

    def __init__(self, game_events, home_team):
        self.home_team = home_team
        self.game_events = game_events
        self.processed_events = []
        self.processed_pulls = []

        self.game_quarter = 0
        self.end_quarter()
        self.home_team_score = 0
        self.away_team_score = 0
        

    def add_event(self, throw_event):
        row = {
            'thrower': throw_event.thrower,
            'thrower_x': throw_event.thrower_x,
            'thrower_y': throw_event.thrower_y,
            'receiver': throw_event.receiver,
            'receiver_x': throw_event.receiver_x,
            'receiver_y': throw_event.receiver_y,
            'turnover': throw_event.turnover,
            'start_on_offense': self.start_on_offense,
            'point_start_time': self.point_start_time,
            'current_line': self.current_line,
            'possession_num': self.possession_num,
            'possession_throw': self.possession_throw,
            'game_quarter': self.game_quarter,
            'quarter_point': self.quarter_point,
            'point_timeouts': self.point_timeouts,
            'coming_from_recording_team_penalty': self.recording_team_penalty,
            'coming_from_opposing_team_penalty': self.opposing_team_penalty,
            'is_home_team': self.home_team,
            'home_team_score': self.home_team_score,
            'away_team_score': self.away_team_score
        }
        self.processed_events.append(row)
        self.recording_team_penalty = 0
        self.opposing_team_penalty = 0

    def add_pull(self, pull_event):
        row = {
            'puller': pull_event.puller,
            'pull_x': pull_event.pull_x,
            'pull_y': pull_event.pull_y,
            'pull_ms': pull_event.pull_ms,
            'home_team_score': self.home_team_score,
            'away_team_score': self.away_team_score
        }
        self.processed_pulls.append(row)

    def end_point(self):
        self.current_line = None
        self.start_on_offense = None
        self.point_start_time = None
        self.possession_num = 0
        self.possession_throw = 0
        self.point_timeouts = 0
        self.recording_team_penalty = 0
        self.opposing_team_penalty = 0
    
    def end_quarter(self):
        self.end_point()
        self.quarter_point = 0
        self.game_quarter = self.game_quarter + 1

class EventHandlers():
    def __init__(self):
        self.event_dict = {1:'start D point', 2:'start O point', 3:'midpoint timeout - recording team', 4:'endpoint timeout - recording team', 5:'midpoint timeout - opposing team',
              6:'endpoint timeout - opposing team', 7:'inbounds pull', 8:'outbounds pull', 9:'offsides - recording team', 10:'offsides - opposing team',
              11:'block', 12:'callahan caught', 13:'throwaway - opposing team', 14:'stall - opposing team', 15:'score - opposing team', 16:'penalty - recording team',
              17:'penalty - opposing team', 18:'pass', 19:'score - recording team', 20:'drop', 21:'dropped pull', 22:'throwaway - recording team', 23:'callahan thrown',
              24:'stall - recording team', 25:'injury', 26:'pmf', 27:'player ejected', 28:'end of first', 29:'end of second', 30:'end of third', 31:'end of fourth', 32:'end of ot',
              33:'end of double ot', 34:'delayed', 35:'postponed'}
        self.handle_function_dict = {'start D point':self.handle_start_D_point, 'start O point':self.handle_start_O_point, 'inbounds pull':self.handle_inbounds_pull, 
                            'score - opposing team':self.handle_score_opposing_team, 'score - recording team':self.handle_score_recording_team, 'pass':self.handle_pass, 'throwaway - recording team':self.handle_throwaway_recording_team,
                            'throwaway - opposing team':self. handle_throwaway_opposing_team, 'block':self.handle_block, 'callahan thrown':self.handle_callahan_thrown,
                            'drop':self.handle_drop, 'end of first':self.handle_end_of_quarter, 'end of second':self.handle_end_of_quarter, 'end of third':self.handle_end_of_quarter,
                            'end of fourth':self.handle_end_of_quarter, 'injury':self.handle_line_change, 'midpoint timeout - opposing team':self.handle_line_change, 'midpoint timeout - recording team':self.handle_line_change,
                            'outbounds pull':self.handle_outbounds_pull, 'penalty - recording team':self.handle_penalty_recording_team, 'penalty - opposing team':self.handle_penalty_opposing_team,
                            'endpoint timeout - recording team':self.handle_endpoint_timeout, 'endpoint timeout - opposing team':self.handle_endpoint_timeout,
                            'offsides - recording team':self.handle_penalty_recording_team, 'offsides - opposing team':self.handle_penalty_opposing_team, 'callahan caught':self.handle_callahan_caught,
                            'stall - opposing team':self.handle_stall_opposing_team, 'stall - recording team':self.handle_stall_opposing_team, 'dropped pull':self.handle_dropped_pull,
                            'pmf':self.handle_pmf, 'player ejected':self.handle_player_ejected, 'end of ot':self.handle_end_of_quarter, 'end of double ot':self.handle_end_of_quarter, 
                            'delayed':self.handle_delayed, 'postponed':self.handle_postponed}

    def start_point(self, team_events: TeamEvents, event: dict, on_offense: bool):
        team_events.current_line = event['line']
        if team_events.possession_num != 0:
            return
        team_events.start_on_offense=on_offense
        team_events.point_start_time = event['time']
        if on_offense:
            team_events.possession_num = 1
        
    def handle_start_D_point(self, team_events: TeamEvents, event: dict):
        self.start_point(team_events, event, False)

    def handle_start_O_point(self, team_events: TeamEvents, event: dict):
        self.start_point(team_events, event, True)

    def handle_inbounds_pull(self, team_events: TeamEvents, event: dict):
        pull_event = team_events.PullEvent(event['puller'], event['pullX'], event['pullY'], event['pullMs'])
        team_events.add_pull(pull_event)

    def handle_outbounds_pull(self, team_events: TeamEvents, event: dict):
        pull_event = team_events.PullEvent(event['puller'])
        team_events.add_pull(pull_event)

    def handle_score_opposing_team(self, team_events: TeamEvents, event: dict):
        team_events.end_point()
        if team_events.home_team:
            team_events.away_team_score = team_events.away_team_score + 1
        else:
            team_events.home_team_score = team_events.home_team_score + 1

    def handle_score_recording_team(self, team_events: TeamEvents, event: dict):
        throw_event = team_events.ThrowEvent(event['thrower'], event['throwerX'], event['throwerY'], event['receiver'], event['receiverX'], event['receiverY'], 0)
        team_events.possession_throw = team_events.possession_throw + 1
        team_events.add_event(throw_event)
        team_events.end_point()
        if team_events.home_team:
            team_events.home_team_score = team_events.home_team_score + 1
        else:
            team_events.away_team_score = team_events.away_team_score + 1
        
    def handle_pass(self, team_events: TeamEvents, event: dict):
        throw_event = team_events.ThrowEvent(event['thrower'], event['throwerX'], event['throwerY'], event['receiver'], event['receiverX'], event['receiverY'], 0)
        team_events.possession_throw = team_events.possession_throw + 1
        team_events.add_event(throw_event)

    def handle_throwaway_recording_team(self, team_events: TeamEvents, event: dict):
        throw_event = team_events.ThrowEvent(event['thrower'], event['throwerX'], event['throwerY'], None, event['turnoverX'], event['turnoverY'], 1)
        team_events.possession_throw = team_events.possession_throw + 1
        team_events.add_event(throw_event)

    def handle_throwaway_opposing_team(self, team_events: TeamEvents, event: dict):
        team_events.possession_num = team_events.possession_num + 1
        team_events.possession_throw = 0

    def handle_block(self, team_events: TeamEvents, event: dict):
        team_events.possession_num = team_events.possession_num + 1
        team_events.possession_throw = 0

    def handle_callahan_thrown(self, team_events: TeamEvents, event: dict):
        throw_event = team_events.ThrowEvent(event['thrower'], event['throwerX'], event['throwerY'], None, event['turnoverX'], event['turnoverY'], 1)
        team_events.add_event(throw_event)
        self.handle_score_opposing_team(team_events, event)

    def handle_drop(self, team_events: TeamEvents, event: dict):
        throw_event = team_events.ThrowEvent(event['thrower'], event['throwerX'], event['throwerY'], event['receiver'], event['receiverX'], event['receiverY'], 1)
        team_events.add_event(throw_event)

    def handle_end_of_quarter(self, team_events: TeamEvents, event: dict):
        team_events.end_quarter()

    def handle_line_change(self, team_events: TeamEvents, event: dict):
        team_events.current_line = event['line']

    def handle_penalty_recording_team(self, team_events: TeamEvents, event: dict):
        team_events.recording_team_penalty = team_events.recording_team_penalty + 1

    def handle_penalty_opposing_team(self, team_events: TeamEvents, event: dict):
        team_events.opposing_team_penalty = team_events.opposing_team_penalty + 1

    def handle_endpoint_timeout(self, team_events: TeamEvents, event: dict):
        pass

    def handle_callahan_caught(self, team_events: TeamEvents, event: dict):
        team_events.end_point()
        if team_events.home_team:
            team_events.home_team_score = team_events.home_team_score + 1
        else:
            team_events.away_team_score = team_events.away_team_score + 1

    def handle_stall_opposing_team(self, team_events: TeamEvents, event: dict):
        team_events.possession_num = team_events.possession_num + 1
        team_events.possession_throw = 0

    def handle_stall_recording_team(self, team_events: TeamEvents, event: dict):
        throw_event = team_events.ThrowEvent(event['thrower'], event['throwerX'], event['throwerY'], None, None, None, 1)
        team_events.possession_throw = team_events.possession_throw + 1
        team_events.add_event(throw_event)

    def handle_dropped_pull(self, team_events: TeamEvents, event: dict):
        pass

    def handle_pmf(self, team_events: TeamEvents, event: dict):
        raise NotImplementedError('pmf event not implemented')

    def handle_player_ejected(self, team_events: TeamEvents, event: dict):
        raise NotImplementedError('player ejected event not implemented')

    def handle_delayed(self, team_events: TeamEvents, event: dict):
        raise NotImplementedError('delayed event not implemented')

    def handle_postponed(self, team_events: TeamEvents, event: dict):
        raise NotImplementedError('postponed event not implemented')

    handle_function_dict = {'start D point':handle_start_D_point, 'start O point':handle_start_O_point, 'inbounds pull':handle_inbounds_pull, 
                            'score - opposing team':handle_score_opposing_team, 'score - recording team':handle_score_recording_team, 'pass':handle_pass, 'throwaway - recording team':handle_throwaway_recording_team,
                            'throwaway - opposing team': handle_throwaway_opposing_team, 'block':handle_block, 'callahan thrown':handle_callahan_thrown,
                            'drop':handle_drop, 'end of first':handle_end_of_quarter, 'end of second':handle_end_of_quarter, 'end of third':handle_end_of_quarter,
                            'end of fourth':handle_end_of_quarter, 'injury':handle_line_change, 'midpoint timeout - opposing team':handle_line_change, 'midpoint timeout - recording team':handle_line_change,
                            'outbounds pull':handle_outbounds_pull, 'penalty - recording team':handle_penalty_recording_team, 'penalty - opposing team':handle_penalty_opposing_team,
                            'endpoint timeout - recording team':handle_endpoint_timeout, 'endpoint timeout - opposing team':handle_endpoint_timeout,
                            'offsides - recording team':handle_penalty_recording_team, 'offsides - opposing team':handle_penalty_opposing_team, 'callahan caught':handle_callahan_caught,
                            'stall - opposing team':handle_stall_opposing_team, 'stall - recording team':handle_stall_opposing_team, 'dropped pull':handle_dropped_pull,
                            'pmf':handle_pmf, 'player ejected':handle_player_ejected, 'end of ot':handle_end_of_quarter, 'end of double ot':handle_end_of_quarter, 
                            'delayed':handle_delayed, 'postponed':handle_postponed}



class GameEvents():
    def __init__(self, gameID: str, proxy: GameEventsProxy):
        self.game_events_proxy = proxy
        self.gameID = gameID
        self.event_handlers = EventHandlers()
        self.home_team = None
        self.away_team = None
        self.get_game_info()
        self.get_game_events()

    def get_game_info(self):
        endpoint = f'games?gameIDs={self.gameID}'
        self.game_events_proxy.get_request(endpoint)
        self.home_teamID = self.game_events_proxy.current_request[0]['homeTeamID']
        self.away_teamID = self.game_events_proxy.current_request[0]['awayTeamID']
        self.start_time = self.game_events_proxy.current_request[0]['startTimestamp']
        self.home_score = self.game_events_proxy.current_request[0]['homeScore']
        self.away_score = self.game_events_proxy.current_request[0]['awayScore']
        
    def get_game_events(self):
        self.game_events_proxy.get_request(f'gameEvents?gameID={self.gameID}')
        self.home_events = self.game_events_proxy.current_request['homeEvents']
        self.away_events = self.game_events_proxy.current_request['awayEvents']

    def process_game_events(self):
        self.home_team = TeamEvents(self.home_events, True)
        assert len(self.home_team.game_events) > 0, "no game events found"
        for event in self.home_team.game_events:
            event_type = self.event_handlers.event_dict[event['type']]
            if event_type not in self.event_handlers.handle_function_dict:
                raise NotImplementedError('event type is not coded yet')
            self.event_handlers.handle_function_dict[event_type](self.home_team, event)
        self.home_team.processed_events = pd.DataFrame(self.home_team.processed_events)

        self.away_team = TeamEvents(self.away_events, False)
        for event in self.away_team.game_events:
            event_type = self.event_handlers.event_dict[event['type']]
            if event_type not in self.event_handlers.handle_function_dict:
                raise NotImplementedError('event type is not coded yet')
            self.event_handlers.handle_function_dict[event_type](self.away_team, event)
        self.away_team.processed_events = pd.DataFrame(self.away_team.processed_events)

    def get_events_df(self, gameID=True, home_team=False, away_team=False, start_time=False, drop_cols=[]):
        if self.home_team is None:
            print('Events not processed yet. Please run process_game_events() first')
            return
        
        # assert self.home_team.home_team_score == self.away_team.home_team_score == self.home_score, "home team scores do not match"
        # assert self.home_team.away_team_score == self.away_team.away_team_score == self.away_score, "away team scores do not match"

        final_df = pd.concat([self.home_team.processed_events, self.away_team.processed_events]).reset_index(drop=True)
        final_df = final_df.drop(drop_cols, axis=1) if len(drop_cols)>0 else final_df
        final_df = final_df.assign(gameID=self.gameID) if gameID else final_df
        final_df = final_df.assign(home_teamID=self.home_teamID) if home_team else final_df
        final_df = final_df.assign(away_teamID=self.away_teamID) if away_team else final_df
        final_df = final_df.assign(start_time=self.start_time) if start_time else final_df
        final_df['total_points'] = final_df['home_team_score'] + final_df['away_team_score']
        return final_df.sort_values(['total_points', 'possession_num', 'start_on_offense', 'possession_throw'], ascending=[True, True, False, True]).drop(['total_points'], axis=1).reset_index(drop=True)


def process_games(dates='2023:'):
    base_url = "https://www.backend.audlstats.com/api/v1/"

    endpoint = f"games?date={dates}"
    ids = pd.DataFrame(requests.get(f'{base_url}{endpoint}').json()['data'])['gameID'].values

    game_events_proxy = GameEventsProxy()
    all_games = []
    for id in ids:
        try:
            game_events = GameEvents(id, game_events_proxy)
            game_events.process_game_events()
            game_df = game_events.get_events_df(True, True, True)
            all_games.append(game_df)
        except AssertionError as e:
            print(id)
            print(e)
        except Exception as e:
            print(id)
            raise e
    return pd.concat(all_games)
