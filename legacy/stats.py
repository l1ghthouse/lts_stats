import pandas as pd
from typing import List


def win_loss(games: pd.DataFrame, by: List[str] = None):
    """
    :param games: the games to calculate the win loss for
    :param by: group on specific columns
    :return: the win loss ratio
    """

    if by is not None:
        grouped_values = games[["result"] + by].value_counts()

        results = pd.concat([
            grouped_values.loc['Win'].rename("Win").astype(float),
            grouped_values.loc['Loss'].rename("Loss").astype(float)], axis=1).fillna(0.0)

        wl_ratio = round(results["Win"].div(results.sum(axis=1)).sort_index()*100, 1).rename("Win/Loss")
        return pd.concat([wl_ratio, rounds_played(games, by)], axis=1)
    else:

        wl_ratio = round((list(games.result).count("Win")/len(games.result))*100, 1)
        rounds = rounds_played(games, by)

        return pd.DataFrame([wl_ratio, rounds], index=["Win/Loss", "Rounds Played"]).T


def rounds_played(games: pd.DataFrame, by: List[str] = None) -> float:
    """
    :param games: the games to calculate the win loss for
    :param by: group on specific columns
    :return: the rounds played
    """

    if by is not None:
        counts = games.groupby(by).count()
        return counts[counts.columns[0]].sort_values(ascending=False).astype(int).rename("Rounds Played")
    else:
        return len(games)


def average_damage(games: pd.DataFrame, by: List[str] = None) -> pd.DataFrame:
    """
    :param games: the games to calculate average damage for
    :param by: group on specific columns
    :return: the average damage per round
    """

    if by is not None:
        damage = round(games[["damageDealt"] + by].groupby(by).mean(), 1)["damageDealt"].rename("Average Damage")
        return pd.concat([damage, rounds_played(games, by)], axis=1)
    else:
        return round(games.damageDealt.mean(), 1)
