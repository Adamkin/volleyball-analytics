import pandas as pd
import streamlit as st

# --- 1. DATA LOADING ---
@st.cache_data
def load_data():
    """Loads and caches all necessary data files."""
    df = pd.read_csv("data/volleyball_clean.csv")
    standings = pd.read_csv("data/league_standings.csv")
    schedule = pd.read_csv("data/volleyball_raw.csv")
    return df, standings, schedule

# --- 2. DATE CLEANING ---
def clean_dutch_date(date_str):
    """Converts Dutch dates (Do 25-sep-'25) to standard format."""
    try:
        month_map = {
            "jan": "01", "feb": "02", "mrt": "03", "apr": "04", "mei": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "okt": "10", "nov": "11", "dec": "12"
        }
        clean_part = date_str.split(' ')[-1].replace("'", "")
        for month_name, month_num in month_map.items():
            if f"-{month_name}-" in clean_part:
                clean_part = clean_part.replace(month_name, month_num)
                break
        return clean_part
    except:
        return None

# --- 3. GAME LOGIC ---
def get_net_sets(row, selected_team):
    """Calculates Set Differential (Won - Lost) for a specific match."""
    try:
        raw_score = row['Uitslag']
        main_score = raw_score.split(' ')[0] # "3-1"
        home_sets = int(main_score.split('-')[0])
        away_sets = int(main_score.split('-')[1])
        
        if row['Thuis'] == selected_team:
            return home_sets - away_sets
        else:
            return away_sets - home_sets
    except:
        return 0

# --- 4. LEAGUE TABLE CALCULATOR ---
def calculate_league_table(df, standings):
    """Calculates the full table including Point Deltas."""
    # 1. Calculate Small Points Delta
    h_s = df.groupby('Thuis')[['Small_Pts_Home', 'Small_Pts_Away']].sum()
    h_s.columns = ['Scored', 'Conceded']
    
    a_s = df.groupby('Gast')[['Small_Pts_Away', 'Small_Pts_Home']].sum()
    a_s.columns = ['Scored', 'Conceded']
    
    t_s = h_s.add(a_s, fill_value=0)
    t_s['Point Delta'] = (t_s['Scored'] - t_s['Conceded']).astype(int)
    
    # 2. Merge with Official Standings
    display_table = standings[['Rank', 'Team', 'Played', 'League_Pts']].copy()
    display_table = display_table.merge(t_s[['Point Delta']], left_on='Team', right_index=True, how='left')
    
    return display_table.sort_values('Rank')