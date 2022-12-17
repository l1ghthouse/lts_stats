import pandas as pd
from typing import List, Union


def map_uid(uid: str, games: pd.DataFrame) -> List[str]:
    """
    :param uid: the user id to map to gamer tags
    :param games: the list of games played
    :return: the associated gamer tags
    """
    return games[games["uid"] == uid]["name"].unique()


def convert_uid_index(frame: Union[pd.DataFrame, pd.Series], games: pd.DataFrame) -> pd.DataFrame:
    """
    :param frame: the frame with uid index to be converted
    :param games: all games played
    :return: gamer tag frame
    """
    new_index = [map_uid(player_id, games)[0] for player_id in frame.index]
    frame.index = new_index

    return frame


def get_total_damage_done_per_round(games: pd.DataFrame) -> pd.Series:
    """
    :param games: all games played
    :return:
    """
    return games[games.columns[
        games.columns.str.contains("damageDealt")]].sum(axis=1)


def get_total_damage_taken_per_round(games: pd.DataFrame) -> pd.Series:
    """
    :param games: all games played
    :return:
    """
    return games[games.columns[
        games.columns.str.contains("damageTaken")]].sum(axis=1)


def get_total_battery_activity(games: pd.DataFrame) -> pd.Series:
    """
    :param games: all games played
    :return:
    """
    return games[games.columns[
        games.columns.str.contains("batteries")]].sum(axis=1)
