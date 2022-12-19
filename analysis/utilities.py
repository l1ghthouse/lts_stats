import pandas as pd


def get_team_size(games: pd.DataFrame) -> pd.DataFrame:
    """
    get the team size for a specific team, match and round, input
    all games played and the result will be a dataframe with index
    match_id, round, team and then a column for the number of players
    on the team
    :param games:   all data stored in mongodb
    :return:        team size, columns are imc and militia, index is matchID and round
    """
    team_size = games.groupby(['matchID', 'round', 'team'])['name'].count().rename('team_size')
    return pd.pivot_table(team_size.reset_index(), index=['matchID', 'round'], columns='team').droplevel(0, axis=1)


def get_damage_dealt(games: pd.DataFrame) -> pd.DataFrame:
    """
    get the damage dealt for the round (not including shield damage)
    :param games:   all data stored in mongodb
    :return:        damage dealt for the round
    """
    return games.groupby(['matchID', 'round'])['damageDealt'].sum()


def get_unique_titan_count(games: pd.DataFrame) -> pd.DataFrame:
    """
    get the titan count for each team for each round, will return 2 if
    2 players are playing Northstar on the same team etc
    :param games:   all data stored in mongodb
    :return:        the number of each titan on each team
    """
    return games.groupby(['matchID', 'round', 'team', 'titan'])['name'].count().rename('count')


def player_names(games: pd.DataFrame) -> dict:
    """
    return a dataframe containing user id, player names and the last
    time that a specific player name was seen associated with the user id
    :param games:   all data stored in the mongo database
    :return:        dictionary containing player id and most recent name
    """
    user_id_frame = games.groupby(['uid', 'name'])['matchTimestamp'].last().reset_index()
    user_id_frame = user_id_frame.rename(
        columns={
            'uid': 'uid',
            'name': 'name',
            'matchTimestamp': 'last_seen'
        }
    ).set_index(['uid', 'name'])
    user_id_frame = user_id_frame.loc[
        user_id_frame.groupby(level=0, group_keys=False)['last_seen'].apply(lambda x: x == x.max())
    ]

    user_id_frame = user_id_frame.reset_index()[['uid', 'name']]
    user_id_dict = user_id_frame.set_index('uid').squeeze().to_dict()

    return user_id_dict


def get_game_type(games: pd.DataFrame) -> pd.DataFrame:
    """
    calculate the team size for a specific round and add it as a column
    :param games:
    :return:
    """
    team_size = games.groupby(['matchID', 'round', 'team'])['name'].count()
    team_size = team_size.rename('team_size').reset_index()

    return pd.merge(
        games,
        team_size,
        left_on=['matchID', 'round', 'team'],
        right_on=['matchID', 'round', 'team']
    )
