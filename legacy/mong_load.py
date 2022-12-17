import os
import pymongo

import pandas as pd
import numpy as np
from tqdm import tqdm


def load_games() -> pd.DataFrame:
    """
    :return: the data for all played games
    """
    client = pymongo.MongoClient(
        os.environ["LIGHTHOUSE_MONGO_KEY"]
    )

    games = pd.DataFrame(list(tqdm(client["ranking"].ranking.find())))

    #games = games.loc[games.ranked & ~games.perfectKits & games.rebalance]
    #games.drop(["rebalance", "ranked", "perfectKits"], inplace=True, axis=1)

    games["team"] = games["team"].replace([2, 3], ["imc", "militia"])
    #games["timeDeathTitan"].replace(0.0, np.nan, inplace=True)
    #games["timeDeathPilot"].replace(0.0, np.nan, inplace=True)

    return games
