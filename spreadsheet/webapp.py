import datetime
import pandas as pd
from streamlit import session_state as state
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode

from database.mongo import load_database
from analysis.preprocess import preprocess
from analysis.utilities import get_game_type


def page_setup() -> None:
    """
    Lighthouse Stats Explorer
    """
    st.set_page_config(
        page_title="Stats Explorer",
        page_icon="https://avatars.githubusercontent.com/u/94710688?s=200&v=4"
    )

    title_image, title_text = st.columns(2)

    with title_text:
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.title("Stats Explorer")

    with title_image:
        st.image(
            "https://avatars.githubusercontent.com/u/94710688?s=200&v=4"
        )


def view_data() -> None:
    """
    view game data
    """
    @st.cache
    def load_game_data() -> pd.DataFrame:
        return get_game_type(preprocess(load_database()))

    ranked_games = load_game_data()

    start_date, end_date = st.columns(2)

    with start_date:
        start_query = datetime.datetime(2022, 1, 1)
        st.date_input(
            "Start Date",
            start_query,
            key="start_date",
            help="The start date of the query",
        )
    with end_date:
        st.date_input("End Date", key="end_date", help="The end date of the query")

    st.multiselect(
        label="Filter Match Type",
        options=sorted(ranked_games.team_size.unique()),
        default=sorted(ranked_games.team_size.unique()),
        key="match_type",
        format_func=lambda match: f"{match}v{match}",
    )
    st.multiselect(
        label="Group Columns",
        options=sorted(ranked_games.columns[ranked_games.dtypes == object]),
        key="group_columns"
    )
    st.multiselect(
        label="Data Columns",
        options=sorted(ranked_games.columns[ranked_games.dtypes != object]),
        key="data_columns"
    )
    st.selectbox(
        label="Aggregation Method",
        options=["sum", "mean", "std", "max", "min"],
        key="agg_func",
        help="sum = all values added together, mean = average per round, std = consistency (high = inconsistent)"
             "max = the maximum value achieved, min = the minimum value achieved"
    )

    if not state.group_columns or not state.data_columns:
        st.stop()

    ranked_games = ranked_games[
        (ranked_games["matchTimestamp"] > state.start_date.strftime("%Y-%m-%d")) &
        (ranked_games["matchTimestamp"] < state.end_date.strftime("%Y-%m-%d"))
    ]
    if not state.match_type:
        st.write("please include a match type")
        st.stop()

    ranked_games = ranked_games[ranked_games.team_size.isin(state.match_type)]

    view_games = ranked_games.groupby(state.group_columns)[state.data_columns].agg(state.agg_func)
    round_count = ranked_games.groupby(
        state.group_columns).count()["team_size"].squeeze().astype(int).rename("rounds_played")
    view_games = pd.concat([view_games, round_count], axis=1)
    view_games = round(view_games, 2)

    st.slider(
        label="Min Rounds Played",
        value=0,
        min_value=0,
        max_value=int(view_games["rounds_played"].max()),
        step=1,
        key="rounds_min"
    )

    wins = ranked_games.groupby(state.group_columns)["result"].value_counts().loc[
        ranked_games.groupby(
            state.group_columns)["result"].value_counts().index.get_level_values(-1) == "Win"].droplevel(-1)
    win_loss = round(wins.div(view_games["rounds_played"]), 2).rename("win_loss")
    view_games = pd.concat([view_games, win_loss.fillna(0.0)], axis=1)
    view_games = view_games[view_games["rounds_played"] > state.rounds_min]
    view_games = view_games.reset_index()

    AgGrid(
        view_games,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
    )


if __name__ == "__main__":

    page_setup()
    view_data()
