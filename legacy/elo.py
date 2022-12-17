import pandas as pd
from sklearn.linear_model import LogisticRegression
from typing import List, Tuple

from utilities import convert_uid_index
import itertools

import warnings
warnings.filterwarnings("ignore")

features = [
    'roundDuration', 'damageDealt', 'damageDealtShields', 'damageDealtTempShields',
    'damageDealtAuto', 'damageDealtPilot', 'damageDealtBlocked', 'critRateDealt',
    'damageTaken', 'damageTakenShields', 'damageTakenTempShields', 'damageTakenAuto',
    'damageTakenBlocked', 'critRateTaken', 'terminationDamage', 'coreFracEarned', 'coresUsed', 'batteriesPicked',
    'batteriesToSelf', 'batteriesToAlly', 'batteriesToAllyPilot', 'shieldsGained', 'tempShieldsGained', 'healthWasted',
    'shieldsWasted', 'timeAsTitan', 'timeAsPilot', 'avgDistanceToAllies', 'avgDistanceToCloseAlly',
    'avgDistanceToEnemies', 'avgDistanceToCloseEnemy', 'avgDistanceToAlliesPilot', 'avgDistanceToCloseAllyPilot',
    'avgDistanceToEnemiesPilot', 'avgDistanceToCloseEnemyPilot', 'distanceTravelled', 'distanceTravelledPilot',
    'damageDealtSelf', 'kills', 'killsPilot', 'terminations'
]


class RankingSystem:

    def __init__(self, games: pd.DataFrame, k: int, g: int = 1, min_matches: int = 15):

        self.historical_rankings = pd.DataFrame()
        self.elo = pd.Series()
        self.k = k
        self.g = g
        self.min_matches = min_matches

        games = games[games['result'] != 'Draw']

        self.games = games

        self.features = games[features].fillna(0.0)
        self.result = games['result'].replace(["Loss", "Win"], [0, 1])

        self.lr = LogisticRegression()
        self.lr.fit(self.features, self.result)

        self.matches_played = pd.Series()

    def process_match(self, match: pd.DataFrame):
        """
        :param match: the match that has been played
        :return:
        """

        for round_played in match.index.unique():
            try:
                self.process_round(match.loc[round_played].fillna(0.0))
            except Exception as e:
                print('could not process match at time {} round {}'.format(match.matchTimestamp, round_played))
                print(e)

        match_played = pd.Series(1, index=match['uid'].unique())
        self.matches_played = self.matches_played.add(match_played, fill_value=0)

        self.historical_rankings = pd.concat(
            [self.historical_rankings, self.elo.rename(len(self.historical_rankings.columns) + 1)],
            axis=1
        )

    def process_round(self, game_round: pd.DataFrame):
        """
        :param game_round: the round that has been played
        :return: the elo changes to make
        """

        winners = game_round[game_round.result == 'Win'].set_index('uid')
        losers = game_round[game_round.result == 'Loss'].set_index('uid')

        for player in game_round['uid'].unique():
            self.check_player(player)

        elo_gained = pd.Series(0, index=game_round['uid'].unique())

        for winner, loser in list(itertools.product(winners.index.values, losers.index.values)):

            prob_win = self.lr.predict_proba(winners.loc[winner][features].values.reshape(-1, 1).T)[0][1]
            prob_loss = self.lr.predict_proba(losers.loc[loser][features].values.reshape(-1, 1).T)[0][0]

            win_gain, lose_loss = self.update_elo(
                winner, loser, prob_win/len(winners.index.values), prob_loss/len(winners.index.values)
            )

            elo_gained[winner] += win_gain
            elo_gained[loser] += lose_loss

        self.elo = self.elo.add(elo_gained, fill_value=0.0)

    def check_player(self, player_id: str):
        """
        :param player_id: the player to add
        """
        if player_id not in self.elo.index:
            self.elo[player_id] = 1000

    def update_elo(self, winner_user_id: str, loser_user_id: str, prob_win: float, prob_loss: float):
        """
        :param winner_user_id: the user id of the winner
        :param loser_user_id: the user id of the loser
        :param prob_win: the probability of the winner having won given their stats
        :param prob_loss: the probability of the loser having lost given their stats
        """
        result = self.expected_result(self.elo[winner_user_id], self.elo[loser_user_id])

        return prob_win*(self.k*self.g)*(1 - result), prob_loss*(self.k*self.g)*(result - 1)

    @staticmethod
    def expected_result(p1, p2) -> float:
        exponent = (p2 - p1) / 400.0
        return 1 / ((10.0 ** exponent) + 1)

    def get_top_10(self) -> pd.DataFrame:
        """
        :return: the current top 10 players
        """
        top = self.elo[self.matches_played > self.min_matches].nlargest(10)

        return convert_uid_index(top.copy(), self.games)

    def get_player_elo(self, player_gt: str) -> float:
        """
        :param player_gt: the player to get elo rating for
        :return: the elo rating of the player
        """
        player_id = self.games[self.games.name == player_gt].uid.unique()[0]

        return self.elo.loc[player_id]

    def create_teams(self, player_gts: List[str]) -> Tuple[List[str], List[str]]:
        """
        :param player_gts: the list of players
        :return: balanced teams by elo
        """
        sorted_players = sorted(player_gts, key=self.get_player_elo)
        team1 = []
        team2 = []
        total_diff = 0

        for p1, p2 in zip(sorted_players[::2], sorted_players[1::2]):
            current_diff = self.get_player_elo(p2) - self.get_player_elo(p1)
            if total_diff * current_diff >= 0:
                team2.append(p1)
                team1.append(p2)
                total_diff -= current_diff
            else:
                team2.append(p2)
                team1.append(p1)
                total_diff += current_diff

        return team1, team2

    def plot_player_elo(self, player_gts: List[str] = None):
        """
        :param player_gts: the list of players to plot for
        """
        plot_data = convert_uid_index(self.historical_rankings.copy(), self.games).T

        if player_gts is not None:
            plot_data[player_gts].plot(figsize=(20, 10))
        else:
            plot_data.plot(figsize=(20, 10))