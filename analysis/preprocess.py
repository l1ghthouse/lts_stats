import numpy as np
import pandas as pd

from analysis.utilities import get_team_size, get_damage_dealt, get_unique_titan_count, player_names


def remove_uneven_teams(games: pd.DataFrame) -> pd.Index:
    """
    get the list of games that had even teams for all matches
    :param games:   all data stored in the mongo database
    :return:        the list of all games that had equal teams
    """
    team_size = get_team_size(games=games)
    max_teams = team_size.groupby('matchID').max()
    valid_games = max_teams[~(team_size["imc"] != team_size["militia"]).groupby('matchID').any()].index

    return valid_games


def remove_no_damage_rounds(games: pd.DataFrame) -> pd.Index:
    """
    get the list of games that have had damage dealt in all rounds
    :param games:   all data stored in the mongo database
    :return:        the list of games that have had damage dealt in all rounds
    """
    damage_dealt = get_damage_dealt(games=games)
    min_damage_dealt = damage_dealt.groupby('matchID').min()
    valid_games = min_damage_dealt[min_damage_dealt != 0].index

    return valid_games


def remove_non_highlander(games: pd.DataFrame) -> pd.Index:
    """
    remove all games that weren't playing highlander in any round
    :param games:   all data stored in the mongo database
    :return:        the list of games that were playing highlander
    """
    titan_count = get_unique_titan_count(games=games)
    titan_count = titan_count.groupby('matchID').max()
    valid_games = titan_count[~(titan_count > 1).groupby('matchID').any()].index

    return valid_games


def preprocess(games: pd.DataFrame) -> pd.DataFrame:
    """
    get all games that should be used for ranking
    :param games:   all data stored in the mongo database
    :return:        the list of games that should be used for ranking
    """
    #ranked_games: pd.DataFrame = games[
    #    games['ranked'] &
    #    games['rebalance'] &
    #    ~games['perfectKits'] &
    #    ~games['isPreRelease'].replace(np.nan, True)
    #].copy()

    #has_even_teams = remove_uneven_teams(games=ranked_games)
    #has_damage = remove_no_damage_rounds(games=ranked_games)
    #has_highlander = remove_non_highlander(games=ranked_games)

    #ranked_games.set_index('matchID', inplace=True)
    #ranked_games = ranked_games.loc[has_even_teams.intersection(has_damage).intersection(has_highlander)]
    ranked_games = games.copy()

    recent_names = player_names(games=ranked_games)
    ranked_games['name'] = ranked_games['uid'].replace(recent_names)

    ranked_games.drop(
        columns=[
            '_id',
            'uid',
            'serverName',
            'ranked',
            'rebalance',
            'perfectKits',
            'isPreRelease',
            'version'
        ],
        inplace=True
    )

    return ranked_games
