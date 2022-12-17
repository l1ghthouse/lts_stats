from utilities import *


def remove_non_players(games: pd.DataFrame) -> pd.DataFrame:
    """
    :param games: the list of all games played
    :return: the list of rows for players that played
    """
    eject_early = (games["timeDeathTitan"] < 10)
    no_damage_done = (games["allDamageDone"] == 0.0)
    no_damage_taken = (games["allDamageTaken"] == 0.0)
    no_activity = (games["batteryActivity"] == 0)

    return games[~(eject_early & no_damage_done & no_activity & no_damage_taken)]


def remove_uneven_teams(games: pd.DataFrame) -> pd.DataFrame:
    """
    :param games: the list of all games played
    :return: the list of rows for all rounds that had equal teams
    """

    team_member_count = games[["matchID", "round", "team", "uid"]].groupby(["matchID", "round", "team"]).count()
    team_member_count = team_member_count["uid"].reset_index(level=2)

    has_equal = (
            team_member_count.groupby(level=[0, 1], axis=0).max()["uid"] ==
            team_member_count.groupby(level=[0, 1], axis=0).min()["uid"]
    )

    return games.set_index(["matchID", "round"]).loc[has_equal].sort_index().reset_index()


def remove_non_highlander(games: pd.DataFrame) -> pd.DataFrame:
    """
    :param games: the list of all games played
    :return: the list of all rows for rounds that ran highlander
    """
    titan_pick_count = games[
        ["matchID", "round", "titan", "uid", "team"]
    ].groupby(["matchID", "round", "titan", "team"]).count()
    titan_pick_count = titan_pick_count["uid"].reset_index(level=[2, 3])

    highlander = (titan_pick_count.groupby(level=[0, 1], axis=0).max()["uid"] == 1)

    return games.set_index(["matchID", "round"]).loc[highlander].sort_index().reset_index()


def remove_no_round_damage(games: pd.DataFrame) -> pd.DataFrame:
    """
    :param games: the list of all games played
    :return: the list of all rows for rounds that ran highlander
    """
    round_damage = games[["matchID", "round", "allDamageDone"]].groupby(["matchID", "round"]).sum()
    round_damage = (round_damage["allDamageDone"] > 0)

    return games.set_index(["matchID", "round"]).loc[round_damage].sort_index().reset_index()


def clean_games(games: pd.DataFrame) -> pd.DataFrame:
    """
    :param games: the dataframe containing all played games
    :return: cleaned game data
    """

    games["allDamageDone"] = get_total_damage_done_per_round(games)
    games["batteryActivity"] = get_total_battery_activity(games)
    games["allDamageTaken"] = get_total_damage_taken_per_round(games)

    active_players = remove_non_players(games)
    even_teams = remove_uneven_teams(active_players)
    non_highlander = remove_non_highlander(even_teams)
    round_damage = remove_no_round_damage(non_highlander)

    return round_damage.set_index(["matchID", "round"])
