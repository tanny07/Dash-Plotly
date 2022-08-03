import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, dash_table
import plotly.express as px
import plotly.graph_objs as go


def get_match_data_set():
    match_dataset = pd.read_csv("data/IPL Matches 2008-2020.csv")
    match_dataset['date'] = pd.to_datetime(match_dataset['date'])
    return match_dataset


def get_matches_played_on_ground(match_dataset, year):
    filtered_dataset = match_dataset[match_dataset['date'].dt.year.isin(year)]
    grounds = filtered_dataset.groupby(['city', 'venue']).size().reset_index()
    grounds.columns = ['city', 'venue', 'No. of Matches']
    grounds_geo_data = pd.read_csv('data/grounds.csv')
    merged_data = pd.merge(grounds, grounds_geo_data, on='venue', how='left')
    merged_data.drop('Unnamed: 0', axis=1, inplace=True)
    return merged_data


def make_toss_data(row):
    if row['toss_winner'] == row['winner']:
        return 1
    else:
        return 0


def get_stadium_statistics(match_dataset, year, stadium):
    ################ DATA FILTERING ########################
    filtered_dataset = match_dataset[(match_dataset['date'].dt.year.isin(year)) & (match_dataset['city'] == stadium)]
    match_ids = filtered_dataset['id'].to_list()
    dataset_byball = pd.read_csv('data/IPL Ball-by-Ball 2008-2020.csv')
    player_dataset = dataset_byball[dataset_byball['id'].isin(match_ids)]

    ################ GENERAL STATS ########################
    team_stats = match_vs_wins(filtered_dataset)

    man_of_the_match_counts = get_man_of_the_match_data(filtered_dataset)
    man_of_the_match_fig = px.bar(
        man_of_the_match_counts.nlargest(10, ['Count']).sort_values(['Count'], ascending=[False]), x='Player',
        y='Count', title="Man of the Match Stats")
    man_of_the_match_fig.update_layout(xaxis_title="Man of the match stats",yaxis_title="count",
                                        legend_title="most wins",font=dict(family="Courier New, monospace",size=14,
                                        color="Black"))
        
    

    toss_win_and_match_win_counts = get_toss_win_and_match_win_data(filtered_dataset)
    toss_win_and_match_win_fig = px.bar(toss_win_and_match_win_counts, x="toss_decision", y="Count",
                                        color="toss_and_match_win", title="Win statistics by match toss")
    toss_win_and_match_win_fig.update_layout(xaxis_title="toss decision",yaxis_title="count",
                                        legend_title="win stats after winning toss",font=dict(family="Courier New, monospace",size=14,
                                        color="Black"))


    ################ BATTING STATS ########################
    team_runs = get_team_runs(player_dataset)
    team_runs_fig = px.sunburst(team_runs, path=['batting_team'], values='total_runs')
    team_runs_fig.update_layout(title="Total Runs by teams ",xaxis_title="Total Overs",yaxis_title="Total Runs",
                                        legend_title="team names with total runs",font=dict(family="Courier New, monospace",size=14,
                                        color="Black"))

    run_types = get_run_types(player_dataset)
    run_types_fig = px.pie(run_types[run_types['total_runs'] > 0], values='batsman_runs', names='total_runs')
    run_types_fig.update_layout(title="Average scoring runs by all teams",legend_title="Game Scores",font=dict(family="Courier New, monospace",size=14,
                                        color="Black"))

    team_over_by_over = get_team_over_by_over_stats(player_dataset)
    team_over_by_over_fig = px.line(team_over_by_over, x="over", y="total_runs", color='batting_team', markers=True)
    team_over_by_over_fig.update_layout(title="Runs scored in each over",xaxis_title="Total Overs",yaxis_title="Total Runs",
                                        legend_title="Team Names",font=dict(family="Courier New, monospace",size=14,
                                        color="Black"))
    


    ################ BOWLING STATS ########################
    wicket_takers = get_top_wicket_takers(player_dataset)
    wicket_takers_fig = px.bar(wicket_takers, x='bowler', y='is_wicket', title="Top wicket takers", color='bowler')
    wicket_takers_fig.update_layout(title="Top wicket takers",xaxis_title="Player Names",yaxis_title="Total Wickets",
                                        legend_title="Highest wicket takers",font=dict(family="Courier New, monospace",size=14,
                                        color="Black"))

    extras = get_extras(player_dataset)
    extras_fig = px.pie(extras, values='count', names='extra_type')
    extras_fig.update_layout(title="Extra runs giving by teams",legend_title="Extra runs",font=dict(family="Courier New, monospace",size=14,
                                        color="Black"))

    dismissal_kind = get_dismissal_kind(player_dataset)
    dismissal_kind_fig = px.bar(dismissal_kind, x='dismissal_kind', y='count')
    dismissal_kind_fig.update_layout(title="Types of batsmen's dismissals",xaxis_title="ways of dismissals",yaxis_title="Count",
                                        legend_title="Team Names",font=dict(family="Courier New, monospace",size=14,
                                        color="Black"))

    layout = html.Div(children=[
        dbc.Row(
            dbc.Col(
                html.H3(filtered_dataset.iloc[0]['venue'] + ' - ' + stadium + ' general stats'),
                width={"size": 6, "offset": 3},
            )
        ),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i}
                             for i in team_stats.columns],
                    data=team_stats.to_dict('records'),
                    style_cell=dict(textAlign='left'),
                    style_header=dict(backgroundColor="paleturquoise"),
                    style_data=dict(backgroundColor="lavender")
                ),
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='man_of_the_match',
                        figure=man_of_the_match_fig
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        id='toss_win',
                        figure=toss_win_and_match_win_fig
                    )
                )
            ]
        ),
        dbc.Row(
            dbc.Col(
                html.H3(filtered_dataset.iloc[0]['venue'] + ' - ' + stadium + ' batting stats'),
                width={"size": 6, "offset": 3},
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='team_runs',
                        figure=team_runs_fig
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        id='run_types',
                        figure=run_types_fig
                    )
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='team_runs_2',
                        figure=team_over_by_over_fig
                    )
                )
            ]
        ),
        dbc.Row(
            dbc.Col(
                html.H3(filtered_dataset.iloc[0]['venue'] + ' - ' + stadium + ' bowling stats'),
                width={"size": 6, "offset": 3},
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='wicket_takers_fig',
                        figure=wicket_takers_fig
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        id='extras_fig',
                        figure=extras_fig
                    )
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='dismissal_kind_fig',
                        figure=dismissal_kind_fig
                    )
                )
            ]
        ),
    ])
    return layout


def match_vs_wins(match_dataset):
    teams = pd.concat([match_dataset['team1'], match_dataset['team2']])
    teams = teams.value_counts().reset_index()
    teams.columns = ['Team', 'Total Matches']
    teams['Wins'] = match_dataset['winner'].value_counts().reset_index()['winner']
    teams['Win percentage(%)'] = ((teams['Wins'] / teams['Total Matches']) * 100).round()

    return teams


def get_man_of_the_match_data(filtered_dataset):
    man_of_the_match_counts = filtered_dataset.groupby(['player_of_match']).size().reset_index()
    man_of_the_match_counts.columns = ['Player', 'Count']
    return man_of_the_match_counts


def get_toss_win_and_match_win_data(filtered_dataset):
    filtered_dataset['toss_and_match_win'] = filtered_dataset.apply(check_winner, axis=1)
    toss = filtered_dataset.groupby(['toss_decision', 'toss_and_match_win']).size().reset_index()
    toss_data = pd.DataFrame(toss)
    toss_data.rename({0: 'Count'}, inplace=True, axis=1)
    return toss_data


def check_winner(row):
    if row['toss_winner'] == row['winner']:
        return 'won'
    else:
        return 'lost'


def get_team_runs(player_dataset):
    matches = player_dataset.groupby(['batting_team'])['total_runs'].agg('sum').reset_index()
    summary = pd.DataFrame(matches)
    return summary


def get_team_over_by_over_stats(player_dataset):
    matches = player_dataset.groupby(['batting_team', 'over'])['total_runs'].agg('sum').reset_index()
    summary = pd.DataFrame(matches)
    return summary


def get_run_types(player_dataset):
    matches = player_dataset.groupby(['total_runs'])['batsman_runs'].agg('sum').reset_index()
    summary = pd.DataFrame(matches)
    return summary


def get_top_wicket_takers(player_dataset):
    wickets = player_dataset[player_dataset['is_wicket'] == 1].groupby(['bowler'])['is_wicket'].agg('sum').reset_index()
    summary = pd.DataFrame(wickets)
    return summary.sort_values(['is_wicket'], ascending=[False])


def get_extras(player_dataset):
    extras = player_dataset.groupby(['extras_type']).size().reset_index()
    summary = pd.DataFrame(extras)
    summary.columns = ['extra_type', 'count']
    return summary


def get_dismissal_kind(player_dataset):
    dismissal_kind = player_dataset.groupby(['dismissal_kind']).size().reset_index()
    summary = pd.DataFrame(dismissal_kind)
    summary.columns = ['dismissal_kind', 'count']
    return summary
