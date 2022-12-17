import os
import pymongo

import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm


def load_database() -> pd.DataFrame:
    """
    :return: the data for all played games
    """
    client = pymongo.MongoClient(
        os.environ["LIGHTHOUSE_MONGO_KEY"],
        tlsAllowInvalidCertificates=True
    )
    games = pd.DataFrame(list(tqdm(client["ranking"].ranking.find())))
    games["team"] = games["team"].replace([2, 3], ["imc", "militia"])

    games['matchTimestamp'] = games['matchTimestamp'].apply(
        lambda date: str(datetime.datetime.fromtimestamp(date).date())
    )

    return games
