import datetime
import pandas as pd
from streamlit import session_state as state
import streamlit as st

from database.mongo import load_database
from analysis.preprocess import preprocess


def page_setup() -> None:
    """
    Lighthouse Stats Explorer
    """
    st.set_page_config(
        page_title="Stats Explorer",
        page_icon='https://avatars.githubusercontent.com/u/94710688?s=200&v=4'
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
        return load_database()

    ranked_games = preprocess(load_game_data())

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
        label='Group Columns',
        options=ranked_games.columns[ranked_games.dtypes == object],
        key='group_columns'
    )
    st.multiselect(
        label='Data Columns',
        options=ranked_games.columns[ranked_games.dtypes != object],
        key='data_columns'
    )
    st.selectbox(
        label='Aggregation Method',
        options=['sum', 'mean', 'std', 'max', 'min'],
        key='agg_func',
    )
    st.multiselect(
        label='View Players (Optional)',
        options=ranked_games.name.unique(),
        key='players'
    )

    if not state.group_columns or not state.data_columns:
        st.stop()

    ranked_games = ranked_games[
        (ranked_games['matchTimestamp'] > state.start_date.strftime("%Y-%m-%d")) &
        (ranked_games['matchTimestamp'] < state.end_date.strftime("%Y-%m-%d"))
    ]

    view_games = ranked_games.groupby(state.group_columns)[state.data_columns].agg(state.agg_func)
    round_count = ranked_games.groupby(
        state.group_columns)['name'].count().squeeze().astype(int).rename('rounds_played')
    view_games = pd.concat([view_games, round_count], axis=1)
    view_games = round(view_games, 2)

    st.slider(
        label='Min Rounds Played',
        value=int(view_games["rounds_played"].min()),
        min_value=int(view_games["rounds_played"].min()),
        max_value=int(view_games["rounds_played"].max()),
        step=1,
        key='rounds_min'
    )
    win_loss = ranked_games.groupby(
        state.group_columns)['result'].value_counts().loc[None:, 'Win'].rename('win_loss')
    win_loss = round(win_loss.div(view_games['rounds_played']), 2).rename('win_loss')
    view_games = pd.concat([view_games, win_loss.fillna(0.0)], axis=1)
    view_games = view_games[view_games['rounds_played'] > state.rounds_min]
    view_games = view_games.reset_index()

    if not state.players:
        st.dataframe(
            view_games,
            use_container_width=True
        )
    else:
        try:
            st.dataframe(
                view_games.set_index('name').loc[state.players].reset_index(),
                use_container_width=True
            )
        except KeyError:
            st.text("no datapoints meet the filter requirements")


if __name__ == '__main__':

    page_setup()
    view_data()
