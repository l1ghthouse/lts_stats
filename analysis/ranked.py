import itertools
import pandas as pd


def get_result(p1, p2) -> float:
    """
    :param p1: the elo of player 1
    :param p2: the elo of player 2
    :return: the expected result of player 1
    """
    exponent = (p2 - p1) / 400.0
    return 1 / ((10.0 ** exponent) + 1)


def update_elo(game_round: pd.DataFrame, k: int, g: int) -> pd.Series:
    """
    update the elo for each player in the game round
    :param game_round:      the game round to update the elo for
    :param elo:             the current elo for each player
    :param k:               the k factor for the elo
    :param g:               the g factor for the elo
    :return:                the updated elo for each player
    """
    try:
        elo = pd.read_csv("database/elo.csv", index_col=0).squeeze()
    except FileNotFoundError:
        elo = pd.Series(dtype=float, name="2021-03-01")

    if game_round.matchTimestamp.unique()[0] < elo.name:
        print("outdated game round")
        return elo

    winners = game_round[game_round['result'] == "Win"]["name"].unique().tolist()
    losers = game_round[game_round['result'] == "Loss"]["name"].unique().tolist()

    for player in winners + losers:
        if player not in elo.index:
            elo[player] = 1000

    winners_elo = elo[winners].mean()
    losers_elo = elo[losers].mean()

    expected_result = get_result(winners_elo, losers_elo)
    loser = (k * g)*(expected_result - 1)
    winner = (k * g) * (1 - expected_result)

    loser_elo_loss = pd.Series(loser, index=losers)
    winner_elo_gain = pd.Series(winner, index=winners)

    elo = elo.add(winner_elo_gain, fill_value=0.0)
    elo = elo.add(loser_elo_loss, fill_value=0.0)

    elo = elo.rename(game_round.matchTimestamp.unique()[0])
    elo.to_csv("database/elo.csv")

    try:
        timeseries_elo = pd.read_csv("database/timeseries_elo.csv", index_col=0)
        timeseries_elo = pd.concat([timeseries_elo, elo], axis=1)
    except FileNotFoundError:
        timeseries_elo = elo

    timeseries_elo.to_csv("database/timeseries_elo.csv")

    return elo


def trigger_update(games: pd.DataFrame) -> None:
    """
    :param games:
    :return:
    """
    try:
        elo = pd.read_csv("database/elo.csv", index_col=0).squeeze()
    except FileNotFoundError:
        elo = pd.Series(dtype=float, name="2021-03-01")

    games = games[games['matchTimestamp'] > elo.name]
    chronological_matches = games.sort_values("matchTimestamp", ascending=True).matchID.unique()

    for match in chronological_matches:

        match_played = games[games["matchID"] == match]
        rounds = match_played["round"].sort_values(ascending=True).unique()

        for round_played in rounds:
            update_elo(
                match_played[match_played["round"] == round_played],
                k=8,
                g=1
            )

