#!/usr/bin/env/python

class Division:
    altantic = 'Atlantic'
    central = 'Central'
    west = 'West'
    canada = 'Canada Cup'


class StatisticsDescription:
    YR = 'Year'
    G = 'Games Played'
    PP = 'Points Played'
    TM = 'Team'
    AST = 'Assists'
    GLS = 'Goals'
    BLK = 'Blocks'
    PLUS_MINUS = 'Plus Minus'
    CMP = 'Completions'
    CMP_PERC = 'Completion Percentage'
    TY = 'Throwing Yards'
    RY = 'Receiving Yards'
    HA = 'Hockey Assists'
    T = 'Throwaways'
    S = 'Stall'
    C = 'Callahan'
    D = 'Drops'
    OPP = 'Offensive Points Played'
    DPP = 'Defensive Points Played'
    P = 'Pulls'


class StatisticAbbreviation:
    stat_col_year = 'YR'
    stat_col_games_played = 'G'
    stat_col_points_played = 'PP'
    stat_col_team = 'TM'
    stat_col_assists = 'AST'
    stat_col_goals = 'GLS'
    stat_col_blocks = 'BLK'
    stat_col_plus_minus = '+/-'
    stat_col_completions = 'CMP'
    stat_col_completion_perc = 'CMP%'
    stat_col_throwing_yards = 'TY'
    stat_col_receiving_yards = 'RY'
    stat_col_hockey_assists = 'HA'
    stat_col_throwaways = 'T'
    stat_col_stalls = 'S'
    stat_col_callahans = 'C'
    stat_col_drops = 'D'
    stat_col_offensive_points_played = 'OPP'
    stat_col_defensive_points_played = 'DPP'
    stat_col_pulls = 'P'


class FileName:
    alltimeplayer = 'AllTimePlayerStats.csv'

#######################################################################
#                          Games Parameters                           #
#######################################################################

# Types of throws and their id :\t on heroku server


class GameEventAction:
    # Types of events defined on heroku server
    # Block
    # Dish
    # Dump
    # Huck throwaway
    # Pass
    # Pull
    # Score
    # Swing
    pass


class TeamStatsName:
    Completions = 'Completions'
    Hucks = 'Hucks'
    Offensive_holds = 'Offensive Holds'
    Defensive_breaks = 'Defensive Breaks'
    Red_zone_possessions = 'Red Zone Posessions'
    Hucks = 'Hucks'
    Turnovers = 'Turnovers'
    Blocks = 'Blocks'
    Turnovers = 'Turnovers'


team_stats_row_names = [
    TeamStatsName.Completions,
    TeamStatsName.Hucks,
    TeamStatsName.Offensive_holds,
    TeamStatsName.Defensive_breaks,
    TeamStatsName.Red_zone_possessions,
    TeamStatsName.Blocks,
    TeamStatsName.Turnovers,
]

team_stats_perc_columns_names = [
    "",
    "Successful",
    "Opportunities",
    "Percentage"
]

# \t: number mapings
# \r: receiver
# \l: lineup
# \x: disc absolute position in x
# \y: disc absolut position in y
# \s: ???
herokuT_dict = {
    '1': 'receiving-pull',
    '2': 'pulling',
    '3': 'throaway-provoked',  # rename?
    #  '5':
    #  '8':
    #  '10':
    #  '12':
    #  '15':
    #  '18',
    #  '19':
    '20': 'pass-completed',
    #  '21':
    '22': 'score',
    #  '23':
    #  '24':
    #  '40':
}


#######################################################################
#                            Miscellaneous                            #
#######################################################################
season_dict = {
    2021: '1',
    2019: '2',
    2018: '3',
    2017: '4',
    2015: '5',
    2016: '6',
    2014: '7',
    2013: '8',
    2012: '9',
}
