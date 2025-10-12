import pandas as pd
import os
from collections import defaultdict
import numpy as np
import requests
from bs4 import BeautifulSoup


def importstats(csv): #imports CSV's via list and organizes them appropriately
    Dataframes=[]

    if not isinstance(csv, list):
        raise TypeError("Expected a List of CSV Files")
    
    for file in csv:
        if not isinstance(file, str):
            raise TypeError(f"List should contain strings of CSV file names. Got {type(file)}: {file}")
        if not file.lower().endswith('.csv'):
            raise ValueError(f"File is not a CSV file: {file}")
        if not os.path.exists(file):
            raise ValueError(f"File not found: {file}")

    for ele in csv:
        importer = pd.read_csv(ele, quotechar="'")
        Dataframes.append(importer)
    for i, df in enumerate(Dataframes):
        df.columns = df.columns.str.replace('"', '', regex=False)
        df['Rk'] = df['Rk'].str.replace('"', '', regex=False)
        df = df.drop(['Rk', 'Day', 'Date', 'Unnamed: 12', 'Opp', 'Result', 'Att', 'Att.1', 'Tgt', 'G#', 'Week','OffSnp'], axis=1)
        df = df.rename(columns={'1D': 'Rush1D', '1D.1': 'Rec1D', 'OffSnp.1': 'OffSnp', 'Att.2': 'PassAtt','TD': 'PassTD', 'Yds': 'PassYds', 'Y/A': 'PassY/A', 'Yds.1': 'SackYds', 'Succ%': 'PassSucc%', 'Att.3': 'RushAtt','TD.1': 'RushTD', 'Yds.2': 'RushYds', 'Y/A/1': 'RushY/A', 'Succ%.1': 'RushSucc%', 'Tgt.1': 'Tgt', 'Yds.3': 'RecYds', 'TD.2': 'RecTD', 'Succ%.2': 'RecSucc%'})

        Dataframes[i] = df


    return Dataframes

def schedulemaker(csv):
    if not isinstance(csv, str):
        raise TypeError(f"Input should be a CSV path to file name as a string. Got {type(csv)}: {csv}")
    if not csv.lower().endswith('.csv'):
        raise ValueError(f"File is not a CSV file: {csv}")
    if not os.path.exists(csv):
        raise ValueError(f"File not found: {csv}")
    
    #NFL Schedule
    Schedule = pd.read_csv(csv)
    Schedule = Schedule.map(lambda x: x.replace('@', '') if isinstance(x, str) else x)

    #Conform to Stathead Labels
    Schedule = Schedule.map(lambda x: x.replace('GB', 'GNB') if isinstance(x, str) else x)
    Schedule = Schedule.map(lambda x: x.replace('KC', 'KAN') if isinstance(x, str) else x)
    Schedule = Schedule.map(lambda x: x.replace('LV', 'LVR') if isinstance(x, str) else x)
    Schedule = Schedule.map(lambda x: x.replace('NO', 'NOR') if isinstance(x, str) else x)
    Schedule = Schedule.map(lambda x: x.replace('NE', 'NWE') if isinstance(x, str) else x)
    Schedule = Schedule.map(lambda x: x.replace('SF', 'SFO') if isinstance(x, str) else x)
    Schedule = Schedule.map(lambda x: x.replace('TB', 'TAM') if isinstance(x, str) else x)
    return Schedule


Combined = pd.DataFrame()
Numeric_Part = pd.DataFrame()
Non_Numeric_Part = pd.DataFrame()
Total_Stats = pd.DataFrame()

def totalstatcombiner(dflist):
    if not isinstance(dflist, list):
        raise TypeError("Expected a List of dataframes Files")
    
    for file in dflist:
        if not isinstance(file, pd.DataFrame):
            raise TypeError(f"List should contain strings of dataframes. Got {type(file)}: {file}")

        
    Combined = pd.concat(dflist, ignore_index=True)
    Numeric_Part = Combined.groupby('Player', as_index=False).sum(numeric_only=True)
    Non_Numeric_Part = Combined.groupby('Player', as_index=False).first(numeric_only=False).drop(columns=Numeric_Part.columns[1:])
    Total_Stats = pd.merge(Numeric_Part, Non_Numeric_Part, on='Player')

    return Total_Stats

def individualtotals(dflist):
    
    if not isinstance(dflist, list):
        raise TypeError("Expected a List of dataframes Files")

    # Collect totals ONLY for games the player played in

    # Initialize a list to collect results
    totals = []
    #teamtotals = []

    # Name of the column with player names
    name_col = "Player"  

    # Use a set to collect unique names
    unique_names = set()

    for df in dflist:
        unique_names.update(df[name_col].dropna().unique())

    # Convert back to list if needed
    unique_names_list = list(unique_names)

    # Loop through each player in Useful
    for player in unique_names_list:
        total_team_pass_att = 0  # Total sum across all DataFrames
        total_team_pass_yards = 0
        total_team_pass_td = 0
        total_team_rec = 0
        total_team_rec_yards = 0
        total_team_rec_td = 0
        total_team_rush_att = 0
        total_team_rush_yards = 0
        total_team_rush_td = 0

        team_total_PA = 0
        team_total_PY = 0
        team_total_PT = 0
        team_total_R = 0
        team_total_RY = 0
        team_total_RT = 0
        team_total_Ru = 0
        team_total_RuY = 0
        team_total_RuT = 0
        
        for df in dflist:
            if player in df['Player'].values:
                # Get the player's team (assumes 1 team per player per df)
                player_team = df.loc[df['Player'] == player, 'Team'].iloc[0]
                #latest_df_with_player = df
                #print(latest_df_with_player.columns)

                # Sum Cmp for all players on the same team
                #player_row = latest_df_with_player[latest_df_with_player['Player'] == player]
                #team_total_PA = latest_df_with_player.loc[latest_df_with_player['Team'] == player_team, 'PassAtt'].sum()
                team_total_PA = df.loc[df['Team'] == player_team, 'PassAtt'].sum()
                team_total_PY = df.loc[df['Team'] == player_team, 'PassYds'].sum()
                team_total_PT = df.loc[df['Team'] == player_team, 'PassTD'].sum()
                team_total_R = df.loc[df['Team'] == player_team, 'Rec'].sum()
                team_total_RY = df.loc[df['Team'] == player_team, 'RecYds'].sum()
                team_total_RT = df.loc[df['Team'] == player_team, 'RecTD'].sum()
                team_total_Ru = df.loc[df['Team'] == player_team, 'RushAtt'].sum()
                team_total_RuY = df.loc[df['Team'] == player_team, 'RushYds'].sum()
                team_total_RuT = df.loc[df['Team'] == player_team, 'RushTD'].sum()

                total_team_pass_att += team_total_PA
                total_team_pass_yards += team_total_PY
                total_team_pass_td += team_total_PT
                total_team_rec += team_total_R
                total_team_rec_yards += team_total_RY
                total_team_rec_td += team_total_RT
                total_team_rush_att += team_total_Ru
                total_team_rush_yards += team_total_RuY
                total_team_rush_td += team_total_RuT

        # Save result
        totals.append({'Player': player, 'TeamTotalPassAtt': total_team_pass_att, 'TeamTotalPassYds': total_team_pass_yards, 'TeamTotalPassTD': total_team_pass_td, 'TeamTotalRec': total_team_rec, 'TeamTotalRecYds': total_team_rec_yards, 'TeamTotalRecTD': total_team_rec_td, 'TeamTotalRushAtt': total_team_rush_att, 'TeamTotalRushYds': total_team_rush_yards, 'TeamTotalRushTD': total_team_rush_td})

    # Create the final result DataFrame
    IndividualTotals = pd.DataFrame(totals)
    return IndividualTotals


def usefulstats(dflist, week, schedule, totalstats, individualtotals):
    if not isinstance(dflist, list):
        raise TypeError("Expected a List of dataframes Files")
    
    for file in dflist:
        if not isinstance(file, pd.DataFrame):
            raise TypeError(f"List should contain strings of dataframes. Got {type(file)}: {file}")
        
    if not isinstance(week, int):
        raise TypeError("int required for Week number")
    
    # Set up Useful Stats Dataframe columns
    Usefulcolumns = ['Player', 'Team', 'Opp', 'Week', 'Pos.', 'G', 'PassAtt', 'PassAttStDev', 'Cmp', 'IndComp%', 'CompStDev', 'TeamComp%', 'PassYds', 'PassYdsStDev', 'PassYds%', 'PassTD', 'PassTDStDev', 'PassTD%','Tgt', 'TgtStDev','Rec', 'IndCatch%', 'CatStDev', 'TmCatch%', 'RecYds', 'RecYdsStDev', 'RecYds%', 'RecTD', 'RecTDStDev', 'RecTD%', 'RushAtt', 'RushStDev', 'Rush%', 'RushYds', 'RushYdsStDev', 'RushYds%', 'RushTD', 'RushTDStDev', 'RushTD%', ]
    Useful = pd.DataFrame(columns=Usefulcolumns)

    # Pre-map Opponents for quick lookup
    schedule_map = {row[0]: row[week] for row in schedule.itertuples(index=False)}

    # Pre-fill columns from Total_Stats if they exist
    for col in Useful.columns:
        if col in totalstats.columns:
            Useful[col] = totalstats[col]


    # Initialize containers for computed values
    stat_fields = ['PassAtt', 'Cmp', 'PassYds', 'PassTD', 'Tgt', 'Rec', 'RecYds', 'RecTD', 'RushAtt', 'RushYds', 'RushTD']

    # Create per-player stat collections
    player_stats = defaultdict(lambda: defaultdict(list))
    player_games_played = defaultdict(int)

    # Precompute all stats from all DataFrames
    for df in dflist:
        if 'Player' not in df.columns:
            continue

        for row in df.itertuples(index=False):
            player = getattr(row, 'Player')

            player_games_played[player] += 1

            for stat in stat_fields:
                if hasattr(row, stat):
                    val = getattr(row, stat)
                    if pd.notnull(val):
                        player_stats[player][stat].append(val)

    # Now update Useful efficiently
    for i, row in Useful.iterrows():
        player = row['Player']
        team = row['Team']

        # Opponent from map
        Useful.at[i, 'Opp'] = schedule_map.get(team, None)

        # Games played
        Useful.at[i, 'G'] = player_games_played.get(player, 0)

        # Standard Deviations
        for stat in stat_fields:
            values = player_stats[player].get(stat, [])
            if len(values) >= 2:
                stdev = np.std(values, ddof=1)
            else:
                stdev = 0

            # Map stat name to your column names in Useful
            stdev_col_map = {
                'PassAtt': 'PassAttStDev',
                'Cmp': 'CompStDev',
                'PassYds': 'PassYdsStDev',
                'PassTD': 'PassTDStDev',
                'Tgt': 'TgtStDev',
                'Rec': 'CatStDev',
                'RecYds': 'RecYdsStDev',
                'RecTD': 'RecTDStDev',
                'RushAtt': 'RushStDev',
                'RushYds': 'RushYdsStDev',
                'RushTD': 'RushTDStDev',
            }

            if stat in stdev_col_map:
                Useful.at[i, stdev_col_map[stat]] = stdev


    Useful = Useful.set_index('Player')
    individualtotals = individualtotals.set_index('Player')

    # Update Individual Completion Percentage
    Useful['IndComp%'] = np.where(Useful['PassAtt'] != 0, (Useful['Cmp'] / Useful['PassAtt']), 0)

    # Update Individual Catch Percentage
    Useful['IndCatch%'] = np.where(Useful['Tgt'] != 0, (Useful['Rec'] / Useful['Tgt']), 0)

    # Update Team Comp Percentage
    Useful['TeamComp%'] = np.where(
        individualtotals['TeamTotalPassAtt'] != 0, (Useful['Cmp'] / individualtotals['TeamTotalPassAtt']), 0)

    # Update Team Pass Yards Percentage
    Useful['PassYds%'] = np.where(
        individualtotals['TeamTotalPassYds'] != 0, (Useful['PassYds'] / individualtotals['TeamTotalPassYds']), 0)

    # Update Team Pass TD Percentage
    Useful['PassTD%'] = np.where(
        individualtotals['TeamTotalPassTD'] != 0, (Useful['PassTD'] / individualtotals['TeamTotalPassTD']), 0)
    Useful['PassTD%'] = Useful['PassTD%'].fillna(0)

    # Update Team Catch Percentage
    Useful['TmCatch%'] = np.where(
        individualtotals['TeamTotalRec'] != 0, (Useful['Rec'] / individualtotals['TeamTotalRec']), 0)

    # Update Team Receiving Yards Percentage
    Useful['RecYds%'] = np.where(
        individualtotals['TeamTotalRecYds'] != 0, (Useful['RecYds'] / individualtotals['TeamTotalRecYds']), 0)

    # Update Team Receiving TD Percentage
    Useful['RecTD%'] = np.where(
        individualtotals['TeamTotalRecTD'] != 0, (Useful['RecTD'] / individualtotals['TeamTotalRecTD']), 0)
    Useful['RecTD%'] = Useful['RecTD%'].fillna(0)

    # Update Team Rush Percentage
    Useful['Rush%'] = np.where(
        individualtotals['TeamTotalRushAtt'] != 0, (Useful['RushAtt'] / individualtotals['TeamTotalRushAtt']), 0)

    # Update Team Rush Yard Percentage
    Useful['RushYds%'] = np.where(
        individualtotals['TeamTotalRushYds'] != 0, (Useful['RushYds'] / individualtotals['TeamTotalRushYds']), 0)

    # Update Team Rush TD Percentage
    Useful['RushTD%'] = np.where(
        individualtotals['TeamTotalRushTD'] != 0, (Useful['RushTD'] / individualtotals['TeamTotalRushTD']), 0)
    Useful['RushTD%'] = Useful['RushTD%'].fillna(0)

    Useful['Week'] = week

    Useful = Useful.reset_index()

    return Useful

def teamtotals(dflist, schedule):
       # Initialize a list to collect results
    teamtotals = []

    # Loop through each player in Useful
    for team in schedule['Team']:
        total_team_completions = 0  # Total sum across all DataFrames
        total_team_pass_yards = 0
        total_team_pass_td = 0
        total_team_rec = 0
        total_team_rec_yards = 0
        total_team_rec_td = 0
        total_team_rush_att = 0
        total_team_rush_yards = 0
        total_team_rush_td = 0

        for df in dflist:
            #if player in df['Player'].values:
                # Get the player's team (assumes 1 team per player per df)
            #team = df.loc[df['Team'] == team, 'Team'].iloc[0]
            matching_team = df.loc[df['Team'] == team, 'Team']
            if not matching_team.empty:
                team = matching_team.iloc[0]  # update only if found
            else:
                pass  # team stays as the last found

            # Sum Cmp for all players on the same team
            team_total_C = df.loc[df['Team'] == team, 'Cmp'].sum()
            team_total_PY = df.loc[df['Team'] == team, 'PassYds'].sum()
            team_total_PT = df.loc[df['Team'] == team, 'PassTD'].sum()
            team_total_R = df.loc[df['Team'] == team, 'Rec'].sum()
            team_total_RY = df.loc[df['Team'] == team, 'RecYds'].sum()
            team_total_RT = df.loc[df['Team'] == team, 'RecTD'].sum()
            team_total_Ru = df.loc[df['Team'] == team, 'RushAtt'].sum()
            team_total_RuY = df.loc[df['Team'] == team, 'RushYds'].sum()
            team_total_RuT = df.loc[df['Team'] == team, 'RushTD'].sum()

            total_team_completions += team_total_C
            total_team_pass_yards += team_total_PY
            total_team_pass_td += team_total_PT
            total_team_rec += team_total_R
            total_team_rec_yards += team_total_RY
            total_team_rec_td += team_total_RT
            total_team_rush_att += team_total_Ru
            total_team_rush_yards += team_total_RuY
            total_team_rush_td += team_total_RuT

        # Save result
        teamtotals.append({'Team': team, 'CmpAAV': total_team_completions, 'PassYdsAAV': total_team_pass_yards, 'PassTDAAV': total_team_pass_td, 'RecAAV': total_team_rec, 'RecYdsAAV': total_team_rec_yards, 'RecTDAAV': total_team_rec_td, 'RushAttAAV': total_team_rush_att, 'RushYdsAAV': total_team_rush_yards, 'RushTDAAV': total_team_rush_td})

    TeamTotals = pd.DataFrame(teamtotals)

    for column in TeamTotals.columns[1:]:
        row_index=0
        
        if (df.iloc[row_index, :len(dflist)] == 'BYE').any():
            TeamTotals[column] = (TeamTotals[column] - TeamTotals[column].mean())/(len(dflist-1))
        else:
            TeamTotals[column] = (TeamTotals[column] - TeamTotals[column].mean())/len(dflist)

    return TeamTotals


def weeklyfinaldataframes(useful, teamtotals):

    #Simulate 10,000 games and average for predictions
    n_simulations = 10000
    team_stats = teamtotals.set_index('Team').to_dict('index')

    statcolumns = ['Player', 'Team', 'PPR', 'STD', 'PassYds', 'PassTD', 'Rec', 'RecYds', 'RecTD', 'RushAtt', 'RushYds', 'RushTD']
    SuperFlex = pd.DataFrame(columns=statcolumns)
    Flex = pd.DataFrame(columns=statcolumns)
    WR = pd.DataFrame(columns=statcolumns)
    RB = pd.DataFrame(columns=statcolumns)
    TE = pd.DataFrame(columns=statcolumns)
    QB = pd.DataFrame(columns=statcolumns)

    #Populate Superflex with Player names
    SuperFlex['Player'] = useful['Player']
    SuperFlex['Team'] = useful['Team']

    #Populate Flex with Player names
    for i, row in useful.iterrows():
        keywords = ['WR', 'RB', 'TE']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            Flex.at[i, 'Player'] = row['Player']

    #Populate WR with Player names
    for i, row in useful.iterrows():
        keywords = ['WR']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            WR.at[i, 'Player'] = row['Player']

    #Populate RB with Player names
    for i, row in useful.iterrows():
        keywords = ['RB']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            RB.at[i, 'Player'] = row['Player']

    #Populate TE with Player names
    for i, row in useful.iterrows():
        keywords = ['TE']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            TE.at[i, 'Player'] = row['Player']

    #Populate QB with Player names
    for i, row in useful.iterrows():
        keywords = ['QB']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            QB.at[i, 'Player'] = row['Player']

    players = []

    predictedrushes = []
    predictedrushyards = []
    predictedrushtds = []

    predictedreceptions = []
    predictedreceivingyards = []
    predictedreceivingtds = []

    predictedpassingyards = []
    predictedpassingtds = []

    pprs = []
    stds = []

    for i, row in useful.iterrows():
        opp = row['Opp']
        rand = np.random.uniform(-2, 2, n_simulations)
        if opp == 'BYE':
            team = 'None'
            rushes = np.zeros(n_simulations)
            rushyards = np.zeros(n_simulations)
            rushtds= np.zeros(n_simulations)

            receptions = np.zeros(n_simulations)
            receivingyards = np.zeros(n_simulations)
            receivingtds = np.zeros(n_simulations)

            passingyards = np.zeros(n_simulations)
            passingtds = np.zeros(n_simulations)
            
        else:
            team = team_stats[opp]

            # Simulations
            rushes = (row['RushAtt'] / row['G']) + row['RushStDev'] * rand + team['RushAttAAV'] * row['Rush%']
            rushyards = (row['RushYds'] / row['G']) + row['RushYdsStDev'] * rand + team['RushYdsAAV'] * row['RushYds%']
            rushtds = (row['RushTD'] / row['G']) + row['RushTDStDev'] * rand + team['RushTDAAV'] * row['RushTD%']

            receptions = (row['Tgt'] / row['G']) * row['IndCatch%'] + row['TgtStDev'] * row['IndCatch%'] * rand + team['RecAAV'] * row['TmCatch%']
            receivingyards = (row['RecYds'] / row['G']) + row['RecYdsStDev'] * rand + team['RecYdsAAV'] * row['RecYds%']
            receivingtds = (row['RecTD'] / row['G']) + row['RecTDStDev'] * rand + team['RecTDAAV'] * row['RecTD%']

            passingyards = (row['PassYds'] / row['G']) + row['PassYdsStDev'] * rand + team['PassYdsAAV'] * row['PassYds%']
            passingtds = (row['PassTD'] / row['G']) + row['PassTDStDev'] * rand + team['PassTDAAV'] * row['PassTD%']

        players.append(row['Player'])

        predictedrushes.append(np.clip(np.round(rushes.mean()).astype(int), 0, None))
        predictedrushyards.append(np.clip(np.round(rushyards.mean()).astype(int), 0, None))
        predictedrushtds.append(np.clip(np.round(rushtds.mean(),1), 0, None))

        predictedreceptions.append(np.clip(np.round(receptions.mean()).astype(int), 0, None))
        predictedreceivingyards.append(np.clip(np.round(receivingyards.mean()).astype(int), 0, None))
        predictedreceivingtds.append(np.clip(np.round(receivingtds.mean(),1), 0, None))

        predictedpassingyards.append(np.clip(np.round(passingyards.mean()).astype(int), 0, None))
        predictedpassingtds.append(np.clip(np.round(passingtds.mean(),1), 0, None))
        

        # Fantasy scoring
        ppr = (
            np.round(rushyards.mean()).astype(int) / 10 +
            np.round(receivingyards.mean()).astype(int) / 10 +
            np.round(passingyards.mean()).astype(int) / 25 +
            np.round(receptions.mean()).astype(int) +
            (np.round(rushtds.mean(),1) + np.round(receivingtds.mean(),1)) * 6 +
            np.round(passingtds.mean(),1) * 4
        )
        pprs.append(ppr)

        std = (
            np.round(rushyards.mean()).astype(int) / 10 +
            np.round(receivingyards.mean()).astype(int) / 10 +
            np.round(passingyards.mean()).astype(int) / 25 +
            (np.round(rushtds.mean(),1) + np.round(receivingtds.mean(),1)) * 6 +
            np.round(passingtds.mean(),1) * 4
        )
        stds.append(std)

    SuperFlex['RushAtt'] = predictedrushes
    SuperFlex['RushYds'] = predictedrushyards
    SuperFlex['RushTD'] = predictedrushtds
    SuperFlex['Rec'] = predictedreceptions
    SuperFlex['RecYds'] = predictedreceivingyards
    SuperFlex['RecTD'] = predictedreceivingtds
    SuperFlex['PassYds'] = predictedpassingyards
    SuperFlex['PassTD'] = predictedpassingtds
    SuperFlex['PPR'] = pprs
    SuperFlex['STD'] = stds
    SuperFlex.iloc[:, 2:4] = SuperFlex.iloc[:, 2:4].apply(pd.to_numeric).round(1)

    #numeric_cols = SuperFlex.select_dtypes(include='number').columns
    #SuperFlex = SuperFlex[:, 4:].clip(lower=0)

    for col in SuperFlex.columns:
        if col != 'Player' and col in Flex.columns:
            Flex[col] = Flex['Player'].map(SuperFlex.set_index('Player')[col])

    for col in SuperFlex.columns:
        if col != 'Player' and col in WR.columns:
            WR[col] = WR['Player'].map(SuperFlex.set_index('Player')[col])

    for col in SuperFlex.columns:
        if col != 'Player' and col in RB.columns:
            RB[col] = RB['Player'].map(SuperFlex.set_index('Player')[col])

    for col in SuperFlex.columns:
        if col != 'Player' and col in TE.columns:
            TE[col] = TE['Player'].map(SuperFlex.set_index('Player')[col])

    for col in SuperFlex.columns:
        if col != 'Player' and col in QB.columns:
            QB[col] = QB['Player'].map(SuperFlex.set_index('Player')[col])

    All_DataFrames = {'SuperFlex': SuperFlex, 'Flex': Flex, 'WR': WR, 'RB': RB, 'TE': TE, 'QB': QB}

    return All_DataFrames


def weeklyhtml(alldataframes, week):
    #html_dict = {}

    for name, df in alldataframes.items():

        html_string = df.to_html(classes='display', index=False).replace('class="dataframe display"', 'class="display"')

        # Full HTML file with sorting and ALL rows shown
        html_script = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>{name} Stats</title>
        <link rel="icon" type="image/png" sizes="96x96" href="images/favicon-96x96.png" />
        <link rel="icon" type="image/svg+xml" href="images/favicon.svg" />
        <link rel="shortcut icon" href="images/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="images/apple-touch-icon.png" />
        <meta name="apple-mobile-web-app-title" content="MyWebSit" />
        <link rel="manifest" href="images/site.webmanifest" />

        <link rel="stylesheet" href="style.css">


        </head>
        <body>

        <div class="topnav">
        <a href="index.html">Home</a>
            <div class="dropdown">
            <button class="dropbtn active">Football
                <i class="fa fa-caret-down"></i>
            </button>
            <div class="dropdown-content">
                <a href="SuperFlex.html">Weekly Predictions</a>
                <a href="Rest Of Season.html">Rest of Season Predictions</a>
            </div>
            </div>
        <a href="fitness.html">Fitness</a>
        <a href="about.html">About</a>
        </div>


        <img src="images/Banner_Logo.png" alt="Header Image" class="header-img">

        <h1>Week {week} {name} Predictions</h1>

        
        <div class="topnav">
        <a {"class='active'" if name == "SuperFlex" else ""} href="SuperFlex.html">SuperFlex</a>
        <a {"class='active'" if name == "Flex" else ""} href="Flex.html">Flex</a>
        <a {"class='active'" if name == "QB" else ""} href="QB.html">QB</a>
        <a {"class='active'" if name == "WR" else ""} href="WR.html">WR</a>
        <a {"class='active'" if name == "RB" else ""} href="RB.html">RB</a>
        <a {"class='active'" if name == "TE" else ""} href="TE.html">TE</a>

        </div>

        
        <div class="topnav">
        <input type="text" id="searchBar" placeholder="Search...">
        </div>


        {html_string}

        <script>
        function getCellValue(row, index) {{
            return row.cells[index].textContent.trim();
        }}

        function comparer(index, asc) {{
            return function(a, b) {{
            const v1 = getCellValue(a, index);
            const v2 = getCellValue(b, index);

            const num1 = parseFloat(v1);
            const num2 = parseFloat(v2);
            const bothNumbers = !isNaN(num1) && !isNaN(num2);

            if (bothNumbers) {{
                return asc ? num1 - num2 : num2 - num1;
            }} else {{
                return asc ? v1.localeCompare(v2) : v2.localeCompare(v1);
            }}
            }};
        }}

        document.addEventListener("DOMContentLoaded", function () {{
            document.querySelectorAll("th").forEach(function (th, index) {{
            let ascending = true;
            th.addEventListener("click", function () {{
                const table = th.closest("table");
                const tbody = table.querySelector("tbody");
                const rows = Array.from(tbody.querySelectorAll("tr"));
                rows.sort(comparer(index, ascending));
                rows.forEach(row => tbody.appendChild(row));
                ascending = !ascending;
            }});
            }});
        }});
        </script>

        

        <script>
        const searchBar = document.getElementById('searchBar');
        const table = document.querySelector('table');
        const rows = table.getElementsByTagName('tr');

        searchBar.addEventListener('keyup', function () {{
            const searchText = searchBar.value.toLowerCase();

            for (let i = 1; i < rows.length; i++) {{
            const row = rows[i];
            const rowText = row.textContent.toLowerCase();
            row.style.display = rowText.includes(searchText) ? '' : 'none';
            }}
        }});
        </script>

        

        </body>
        </html>
        """

        # Save to HTML file
        with open(f"{name}.html", "w") as f:
            f.write(html_script)


def injuryremoval(useful):
    #Erasing Injured Players from DataFrames using ESPN

    # URL of the website you want to scrape
    url = 'https://www.espn.com/nfl/injuries'

    # Send an HTTP GET request to the URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/',  # optional, but can help
        'Accept-Language': 'en-US,en;q=0.9',
    }

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    # Get all team name spans
    team_spans = soup.find_all("span", class_="injuries__teamName")

    # Get all tables (assumed in same order as teams)
    tables = soup.find_all("table")
    hurtplayers = []
    # Loop through team/table pairs
    for team_span, table in zip(team_spans, tables):

        # Extract headers
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

        # Extract rows
        rows = table.find_all("tr")[1:]  # skip header row
        for row in rows:
            cols = row.find_all("td")
            if len(cols) != len(headers):
                continue  # skip malformed rows
            data = {}
            for i in range(len(headers)):
                # If it's a link (e.g. player name), get the text
                link = cols[i].find("a")
                text = link.get_text(strip=True) if link else cols[i].get_text(strip=True)
                data[headers[i]] = text
            hurtplayers.append(data)


    #List_All_Dataframes = [SuperFlex, Flex, WR, RB, TE, QB]

    IR_Players = [
        player['name']
        for player in hurtplayers
        if player.get('status') in ['Out', 'Injured Reserve']
    ]


    #print(IR_Players)

    Useful = useful[~useful['Player'].isin(IR_Players)]
    #SuperFlex = SuperFlex[~SuperFlex['Player'].isin(IR_Players)]
    #Flex = Flex[~Flex['Player'].isin(IR_Players)]
    #WR = WR[~WR['Player'].isin(IR_Players)]
    #RB = RB[~RB['Player'].isin(IR_Players)]
    #TE = TE[~TE['Player'].isin(IR_Players)]
    #QB = QB[~QB['Player'].isin(IR_Players)]

    return Useful



def rosfinaldataframes(useful, teamtotals, week, schedule):

    statcolumns = ['Player', 'Team', 'PPR', 'STD', 'PassYds', 'PassTD', 'Rec', 'RecYds', 'RecTD', 'RushAtt', 'RushYds', 'RushTD']
    Flex_ROS = pd.DataFrame(columns=statcolumns)
    WR_ROS = pd.DataFrame(columns=statcolumns)
    RB_ROS = pd.DataFrame(columns=statcolumns)
    TE_ROS = pd.DataFrame(columns=statcolumns)
    QB_ROS = pd.DataFrame(columns=statcolumns)

    # Prepare your output DataFrame
    ROS = pd.DataFrame()
    ROS['Player'] = useful['Player']

    #Populate Flex with Player names
    for i, row in useful.iterrows():
        keywords = ['WR', 'RB', 'TE']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            Flex_ROS.at[i, 'Player'] = row['Player']

    #Populate WR with Player names
    for i, row in useful.iterrows():
        keywords = ['WR']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            WR_ROS.at[i, 'Player'] = row['Player']

    #Populate RB with Player names
    for i, row in useful.iterrows():
        keywords = ['RB']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            RB_ROS.at[i, 'Player'] = row['Player']

    #Populate TE with Player names
    for i, row in useful.iterrows():
        keywords = ['TE']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            TE_ROS.at[i, 'Player'] = row['Player']

    #Populate QB with Player names
    for i, row in useful.iterrows():
        keywords = ['QB']
        if any(kw.lower() in row['Pos.'].lower() for kw in keywords):
            QB_ROS.at[i, 'Player'] = row['Player']

    stats = [col for col in statcolumns if col != 'Player']

    # Initialize projection columns to 0
    for stat in stats:
        ROS[stat] = 0

    #Simulate 10,000 games and average for predictions then add them for ROS
    n_simulations = 10000
    team_stats = teamtotals.set_index('Team').to_dict('index')


    for week in range(week, 18):

        players = []

        predictedrushes = []
        predictedrushyards = []
        predictedrushtds = []

        predictedreceptions = []
        predictedreceivingyards = []
        predictedreceivingtds = []

        predictedpassingyards = []
        predictedpassingtds = []

        pprs = []
        stds = []

        schedule_map = {row[0]: row[week] for row in schedule.itertuples(index=False)}
        for i, row in useful.iterrows():

            team = row['Team']
            opp = schedule_map.get(team, 'BYE')
            rand = np.random.uniform(-2, 2, n_simulations)
            if opp == 'BYE':
                
                rushes = np.zeros(n_simulations)
                rushyards = np.zeros(n_simulations)
                rushtds= np.zeros(n_simulations)

                receptions = np.zeros(n_simulations)
                receivingyards = np.zeros(n_simulations)
                receivingtds = np.zeros(n_simulations)

                passingyards = np.zeros(n_simulations)
                passingtds = np.zeros(n_simulations)
                
            else:
                team = team_stats[opp]
                
                # Simulations
                rushes = (row['RushAtt'] / row['G']) + row['RushStDev'] * rand + team['RushAttAAV'] * row['Rush%']
                rushyards = (row['RushYds'] / row['G']) + row['RushYdsStDev'] * rand + team['RushYdsAAV'] * row['RushYds%']
                rushtds = (row['RushTD'] / row['G']) + row['RushTDStDev'] * rand + team['RushTDAAV'] * row['RushTD%']

                receptions = (row['Tgt'] / row['G']) * row['IndCatch%'] + row['TgtStDev'] * row['IndCatch%']* rand + team['RecAAV'] * row['TmCatch%']
                receivingyards = (row['RecYds'] / row['G']) + row['RecYdsStDev'] * rand + team['RecYdsAAV'] * row['RecYds%']
                receivingtds = (row['RecTD'] / row['G']) + row['RecTDStDev'] * rand + team['RecTDAAV'] * row['RecTD%']

                passingyards = (row['PassYds'] / row['G']) + row['PassYdsStDev'] * rand + team['PassYdsAAV'] * row['PassYds%']
                passingtds = (row['PassTD'] / row['G']) + row['PassTDStDev'] * rand + team['PassTDAAV'] * row['PassTD%']

            players.append(row['Player'])

            predictedrushes.append(np.clip(np.round(rushes.mean()).astype(int), 0, None))
            predictedrushyards.append(np.clip(np.round(rushyards.mean()).astype(int), 0, None))
            predictedrushtds.append(np.clip(np.round(rushtds.mean(),1), 0, None))

            predictedreceptions.append(np.clip(np.round(receptions.mean()).astype(int), 0, None))
            predictedreceivingyards.append(np.clip(np.round(receivingyards.mean()).astype(int), 0, None))
            predictedreceivingtds.append(np.clip(np.round(receivingtds.mean(),1), 0, None))

            predictedpassingyards.append(np.clip(np.round(passingyards.mean()).astype(int), 0, None))
            predictedpassingtds.append(np.clip(np.round(passingtds.mean(),1), 0, None))
            

            # Fantasy scoring
            ppr = (
                np.round(rushyards.mean()).astype(int) / 10 +
                np.round(receivingyards.mean()).astype(int) / 10 +
                np.round(passingyards.mean()).astype(int) / 25 +
                np.round(receptions.mean()).astype(int) +
                (np.round(rushtds.mean(),1) + np.round(receivingtds.mean(),1)) * 6 +
                np.round(passingtds.mean(),1) * 4
            )
            pprs.append(ppr)

            std = (
                np.round(rushyards.mean()).astype(int) / 10 +
                np.round(receivingyards.mean()).astype(int) / 10 +
                np.round(passingyards.mean()).astype(int) / 25 +
                (np.round(rushtds.mean(),1) + np.round(receivingtds.mean(),1)) * 6 +
                np.round(passingtds.mean(),1) * 4
            )
            stds.append(std)


        ROS['RushAtt'] += predictedrushes
        ROS['RushYds'] += predictedrushyards
        ROS['RushTD'] += predictedrushtds
        ROS['Rec'] += predictedreceptions
        ROS['RecYds'] += predictedreceivingyards
        ROS['RecTD'] += predictedreceivingtds
        ROS['PassYds'] += predictedpassingyards
        ROS['PassTD'] += predictedpassingtds
        ROS['PPR'] += pprs
        ROS['STD'] += stds
        ROS.iloc[:, 2:4] = ROS.iloc[:, 2:4].apply(pd.to_numeric).round(1)

    ROS['Team'] = useful['Team']


    for col in ROS.columns:
        if col != 'Player' and col in Flex_ROS.columns:
            Flex_ROS[col] = Flex_ROS['Player'].map(ROS.set_index('Player')[col])

    for col in ROS.columns:
        if col != 'Player' and col in WR_ROS.columns:
            WR_ROS[col] = WR_ROS['Player'].map(ROS.set_index('Player')[col])

    for col in ROS.columns:
        if col != 'Player' and col in RB_ROS.columns:
            RB_ROS[col] = RB_ROS['Player'].map(ROS.set_index('Player')[col])

    for col in ROS.columns:
        if col != 'Player' and col in TE_ROS.columns:
            TE_ROS[col] = TE_ROS['Player'].map(ROS.set_index('Player')[col])

    for col in ROS.columns:
        if col != 'Player' and col in QB_ROS.columns:
            QB_ROS[col] = QB_ROS['Player'].map(ROS.set_index('Player')[col])

    All_DataFrames = {'Rest Of Season': ROS, 'Flex ROS': Flex_ROS, 'WR ROS': WR_ROS, 'RB ROS': RB_ROS, 'TE ROS': TE_ROS, 'QB ROS': QB_ROS}

    return All_DataFrames


def roshtml(alldataframes):
    #html_dict = {}

    for name, df in alldataframes.items():

        html_string = df.to_html(classes='display', index=False).replace('class="dataframe display"', 'class="display"')

        # Full HTML file with sorting and ALL rows shown
        html_script = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>{name} Stats</title>
        <link rel="icon" type="image/png" sizes="96x96" href="images/favicon-96x96.png" />
        <link rel="icon" type="image/svg+xml" href="images/favicon.svg" />
        <link rel="shortcut icon" href="images/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="images/apple-touch-icon.png" />
        <meta name="apple-mobile-web-app-title" content="MyWebSit" />
        <link rel="manifest" href="images/site.webmanifest" />

        <link rel="stylesheet" href="style.css">


        </head>
        <body>

        <div class="topnav">
        <a href="index.html">Home</a>
            <div class="dropdown">
            <button class="dropbtn active">Football
                <i class="fa fa-caret-down"></i>
            </button>
            <div class="dropdown-content">
                <a href="SuperFlex.html">Weekly Predictions</a>
                <a href="Rest Of Season.html">Rest of Season Predictions</a>
            </div>
            </div>
        <a href="fitness.html">Fitness</a>
        <a href="about.html">About</a>
        </div>
        

        <img src="images/Banner_Logo.png" alt="Header Image" class="header-img">

        <h1>{name} Predictions</h1>

        
        <div class="topnav">
        <a {"class='active'" if name == "Rest Of Season" else ""} href="Rest Of Season.html">Rest Of Season</a>
        <a {"class='active'" if name == "QB ROS" else ""} href="QB ROS.html">QB ROS</a>
        <a {"class='active'" if name == "WR ROS" else ""} href="WR ROS.html">WR ROS</a>
        <a {"class='active'" if name == "RB ROS" else ""} href="RB ROS.html">RB ROS</a>
        <a {"class='active'" if name == "TE ROS" else ""} href="TE ROS.html">TE ROS</a>

        </div>

        <div class="topnav">
        <input type="text" id="searchBar" placeholder="Search...">
        </div>





        {html_string}

        <script>
        function getCellValue(row, index) {{
            return row.cells[index].textContent.trim();
        }}

        function comparer(index, asc) {{
            return function(a, b) {{
            const v1 = getCellValue(a, index);
            const v2 = getCellValue(b, index);

            const num1 = parseFloat(v1);
            const num2 = parseFloat(v2);
            const bothNumbers = !isNaN(num1) && !isNaN(num2);

            if (bothNumbers) {{
                return asc ? num1 - num2 : num2 - num1;
            }} else {{
                return asc ? v1.localeCompare(v2) : v2.localeCompare(v1);
            }}
            }};
        }}

        document.addEventListener("DOMContentLoaded", function () {{
            document.querySelectorAll("th").forEach(function (th, index) {{
            let ascending = true;
            th.addEventListener("click", function () {{
                const table = th.closest("table");
                const tbody = table.querySelector("tbody");
                const rows = Array.from(tbody.querySelectorAll("tr"));
                rows.sort(comparer(index, ascending));
                rows.forEach(row => tbody.appendChild(row));
                ascending = !ascending;
            }});
            }});
        }});
        </script>

        

        <script>
        const searchBar = document.getElementById('searchBar');
        const table = document.querySelector('table');
        const rows = table.getElementsByTagName('tr');

        searchBar.addEventListener('keyup', function () {{
            const searchText = searchBar.value.toLowerCase();

            for (let i = 1; i < rows.length; i++) {{
            const row = rows[i];
            const rowText = row.textContent.toLowerCase();
            row.style.display = rowText.includes(searchText) ? '' : 'none';
            }}
        }});
        </script>

        

        </body>
        </html>
        """

        # Save to HTML file
        with open(f"{name}.html", "w") as f:
            f.write(html_script)



