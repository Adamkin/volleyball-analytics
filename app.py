import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import utils  # <--- Importing your new module

# --- PAGE CONFIG ---
st.set_page_config(page_title="Volleyball Analytics", page_icon="🏐", layout="wide")

# --- LOAD DATA (Using Utils) ---
df, standings, schedule = utils.load_data()

# --- SIDEBAR ---
st.sidebar.header("🎯 Team Selector")
try:
    default_ix = list(standings['Team']).index("ABC Volleybal 3")
except:
    default_ix = 0
selected_team = st.sidebar.selectbox("Select Team:", standings['Team'].unique(), index=default_ix)

# --- MAIN PAGE ---
st.title(f"🏐 Analyst Report: {selected_team}")

# 1. TOP METRICS
team_stats = standings[standings['Team'] == selected_team].iloc[0]

# --- Calculate Sets Won (Since it's not in the CSV) ---
my_games = schedule[
    ((schedule['Thuis'] == selected_team) | (schedule['Gast'] == selected_team)) & 
    (schedule['Uitslag'].notna())
]

def count_sets(row):
    try:
        score = row['Uitslag'].split(' ')[0] # Get "3-1"
        home, away = map(int, score.split('-'))
        return home if row['Thuis'] == selected_team else away
    except:
        return 0

total_sets_won = my_games.apply(count_sets, axis=1).sum()
# ------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Position", f"#{team_stats['Rank']}")
col2.metric("League Points", team_stats['League_Pts'])
#col3.metric("Sets Won", total_sets_won)              # <--- Uses calculated variable now
col3.metric("Points Per Match", f"{team_stats['PPM']:.2f}")

# NEW: Clean League Table (Logic moved to utils)
with st.expander("🏆 View Full League Standings"):
    display_table = utils.calculate_league_table(df, standings)
    display_table.columns = ['#', 'Team', 'Matches', 'Points', 'Point Delta'] 

    def highlight_team(row):
        # Change to rgba(255, 215, 0, 0.2) -> 20% transparent gold
        # This works on BOTH dark mode (white text) and light mode (black text)
        if row['Team'] == selected_team:
            return ['background-color: rgba(255, 215, 0, 0.2)'] * len(row)
        else:
            return [''] * len(row)
            
    st.dataframe(display_table.style.apply(highlight_team, axis=1), hide_index=True, use_container_width=True)

st.divider()

# 2. NEXT MATCH PREDICTOR
st.subheader("🔮 Next Match Forecast")
future_matches = schedule[((schedule['Thuis'] == selected_team) | (schedule['Gast'] == selected_team)) & (schedule['Uitslag'].isna())]

if len(future_matches) > 0:
    next_match = future_matches.iloc[0]
    is_home = next_match['Thuis'] == selected_team
    opponent = next_match['Gast'] if is_home else next_match['Thuis']
    loc = "🏠 Home" if is_home else "🚌 Away"
    
    try:
        opp_ppm = standings[standings['Team'] == opponent].iloc[0]['PPM']
    except:
        opp_ppm = 0.0
        
    my_ppm = team_stats['PPM']
    diff = my_ppm - opp_ppm
    
    if diff > 0.8: pred, color = "3-0 (Win)", "green"
    elif diff > 0.1: pred, color = "2-1 (Win)", "lightgreen"
    elif diff > -0.8: pred, color = "1-2 (Loss)", "orange"
    else: pred, color = "0-3 (Loss)", "red"
    
    c1, c2, c3 = st.columns(3)
    c1.info(f"**Vs:** {opponent}")
    c2.info(f"**Loc:** {loc}")
    c3.info(f"**Date:** {next_match['Datum']}")
    st.markdown(f"### 🤖 AI Prediction: :{color}[{pred}]")
    
    total_strength = my_ppm + opp_ppm
    win_prob = my_ppm / total_strength if total_strength > 0 else 0.5
    st.progress(win_prob)
    st.caption(f"Win Probability: {win_prob*100:.1f}%")
else:
    st.success("Season Completed! 🎉")

st.divider()

# 3. THE MONEYBALL CHART
st.subheader("📊 League Landscape")
# Note: Stats are calculated via utils logic or raw DF here.
# Re-calculating for plotting flexibility:
home_stats = df.groupby('Thuis')[['Small_Pts_Home', 'Small_Pts_Away']].sum()
away_stats = df.groupby('Gast')[['Small_Pts_Away', 'Small_Pts_Home']].sum()
home_stats.columns = ['Scored', 'Conceded']
away_stats.columns = ['Scored', 'Conceded']
total_stats = home_stats.add(away_stats, fill_value=0)

fig, ax = plt.subplots(figsize=(10, 6))

# A. Split the data
if selected_team in total_stats.index:
    # Everyone ELSE
    others = total_stats[total_stats.index != selected_team]
    # My Team
    my_team_data = total_stats.loc[[selected_team]]
else:
    others = total_stats
    my_team_data = None

# B. Plot "Others" (Grey, standard size)
ax.scatter(others['Conceded'], others['Scored'], color='#bdc3c7', s=100, alpha=0.6)

# Label "Others"
for team_name, row in others.iterrows():
    ax.text(row['Conceded']+1, row['Scored']+1, team_name, fontsize=8, alpha=0.6, color='gray')

# C. Plot "My Team" (Red, SAME size, no grey underneath)
if my_team_data is not None:
    ax.scatter(my_team_data['Conceded'], my_team_data['Scored'], color='#e74c3c', s=100, zorder=10)
    # Bold Red Label
    ax.text(my_team_data['Conceded'].iloc[0]+1, my_team_data['Scored'].iloc[0]+1, selected_team, fontsize=10, fontweight='bold', color='#c0392b')

# Averages and Grid
ax.axhline(total_stats['Scored'].mean(), color='green', linestyle='--', alpha=0.3)
ax.axvline(total_stats['Conceded'].mean(), color='blue', linestyle='--', alpha=0.3)

ax.set_xlabel("Points Conceded (Right is Better)")
ax.set_ylabel("Points Scored (Top is Better)")
ax.invert_xaxis()
ax.grid(True, linestyle=':', alpha=0.3)

st.pyplot(fig)

st.divider()

# 4. SEASON MOMENTUM
st.subheader("📈 Season Momentum")
my_matches = schedule[((schedule['Thuis'] == selected_team) | (schedule['Gast'] == selected_team)) & (schedule['Uitslag'].notna())].copy()

# CLEANING via UTILS
my_matches['Datum_Clean'] = my_matches['Datum'].apply(utils.clean_dutch_date)
my_matches['Datum'] = pd.to_datetime(my_matches['Datum_Clean'], format='%d-%m-%y')
my_matches = my_matches.sort_values('Datum')

# CALCULATION via UTILS (Pass selected_team as argument)
my_matches['Net_Sets'] = my_matches.apply(lambda row: utils.get_net_sets(row, selected_team), axis=1)
my_matches['Team Performance'] = my_matches['Net_Sets'].cumsum()

st.line_chart(my_matches, x='Datum', y='Team Performance')
st.caption("📈 Rising Line = Winning more sets than losing. 📉 Falling Line = Losing more sets.")