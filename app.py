import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Volleyball Analytics", page_icon="🏐", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Load your existing clean data
    df = pd.read_csv("data/volleyball_clean.csv")
    standings = pd.read_csv("data/league_standings.csv")
    schedule = pd.read_csv("data/volleyball_raw.csv")
    return df, standings, schedule

df, standings, schedule = load_data()

# --- SIDEBAR ---
st.sidebar.header("🎯 Team Selector")
# Default to your team
try:
    default_ix = list(standings['Team']).index("ABC Volleybal 3")
except:
    default_ix = 0
    
selected_team = st.sidebar.selectbox("Select Team:", standings['Team'].unique(), index=default_ix)

# --- MAIN PAGE ---
st.title(f"🏐 Analyst Report: {selected_team}")

# 1. TOP METRICS
team_stats = standings[standings['Team'] == selected_team].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Position", f"#{team_stats['Rank']}")
col2.metric("League Points", team_stats['League_Pts']) # Fixed Name
col3.metric("Sets Won", team_stats['Scored'])          # Fixed Name
col4.metric("Points Per Match", f"{team_stats['PPM']:.2f}")

st.divider()

# 2. NEXT MATCH PREDICTOR
st.subheader("🔮 Next Match Forecast")

future_matches = schedule[
    ((schedule['Thuis'] == selected_team) | (schedule['Gast'] == selected_team)) & 
    (schedule['Uitslag'].isna())
]

if len(future_matches) > 0:
    next_match = future_matches.iloc[0]
    
    if next_match['Thuis'] == selected_team:
        opponent = next_match['Gast']
        loc = "🏠 Home"
    else:
        opponent = next_match['Thuis']
        loc = "🚌 Away"
    
    # Get Opponent Stats
    try:
        opp_stats = standings[standings['Team'] == opponent].iloc[0]
        opp_ppm = opp_stats['PPM']
    except:
        opp_ppm = 0.0 # Default if not found
        
    my_ppm = team_stats['PPM']
    
    # Prediction Logic
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
    
    # Win Probability
    total_strength = my_ppm + opp_ppm
    if total_strength > 0:
        win_prob = my_ppm / total_strength
    else:
        win_prob = 0.5
        
    st.progress(win_prob)
    st.caption(f"Win Probability: {win_prob*100:.1f}%")

else:
    st.success("Season Completed! 🎉")

st.divider()

# 3. THE MONEYBALL CHART
st.subheader("📊 League Landscape")

home_stats = df.groupby('Thuis')[['Small_Pts_Home', 'Small_Pts_Away']].sum()
away_stats = df.groupby('Gast')[['Small_Pts_Away', 'Small_Pts_Home']].sum()
home_stats.columns = ['Scored', 'Conceded']
away_stats.columns = ['Scored', 'Conceded']
total_stats = home_stats.add(away_stats, fill_value=0)

fig, ax = plt.subplots(figsize=(10, 6))
# Plot everyone
ax.scatter(total_stats['Conceded'], total_stats['Scored'], color='#bdc3c7', s=100, alpha=0.5)

# Highlight Selected Team
if selected_team in total_stats.index:
    team_data = total_stats.loc[selected_team]
    ax.scatter(team_data['Conceded'], team_data['Scored'], color='#e74c3c', s=200, zorder=10)
    ax.text(team_data['Conceded']-2, team_data['Scored']+5, selected_team, fontsize=12, fontweight='bold', color='#c0392b')

# Averages
ax.axhline(total_stats['Scored'].mean(), color='green', linestyle='--', alpha=0.3)
ax.axvline(total_stats['Conceded'].mean(), color='blue', linestyle='--', alpha=0.3)

ax.set_xlabel("Points Conceded (Right is Better)")
ax.set_ylabel("Points Scored (Top is Better)")
ax.invert_xaxis()
ax.grid(True, linestyle=':', alpha=0.3)

st.pyplot(fig)

st.divider()

# 4. SEASON MOMENTUM (New Feature)
st.subheader("📈 Season Momentum")

# Filter matches for the selected team that are already played
my_matches = schedule[
    ((schedule['Thuis'] == selected_team) | (schedule['Gast'] == selected_team)) & 
    (schedule['Uitslag'].notna())
].copy()

# --- DATE CLEANING HELPER ---
def clean_dutch_date(date_str):
    # Example Input: "Do 25-sep-'25"
    try:
        # 1. Map Dutch months to numbers
        month_map = {
            "jan": "01", "feb": "02", "mrt": "03", "apr": "04", "mei": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "okt": "10", "nov": "11", "dec": "12"
        }
        
        # 2. Get the date part (Remove the "Do " or "Za " prefix)
        # Split by space and take the last part: "25-sep-'25"
        clean_part = date_str.split(' ')[-1]
        
        # 3. Remove the apostrophe: "25-sep-25"
        clean_part = clean_part.replace("'", "")
        
        # 4. Swap month name for number: "25-09-25"
        for month_name, month_num in month_map.items():
            if f"-{month_name}-" in clean_part:
                clean_part = clean_part.replace(month_name, month_num)
                break
                
        return clean_part
    except:
        return None

# Apply the cleaner
my_matches['Datum_Clean'] = my_matches['Datum'].apply(clean_dutch_date)

# Convert to DateTime object (Format: Day-Month-Year(2digit))
my_matches['Datum'] = pd.to_datetime(my_matches['Datum_Clean'], format='%d-%m-%y')
# --- END CLEANING ---

my_matches = my_matches.sort_values('Datum')

# Updated Function: Calculates Net Difference (Won - Lost)
def get_net_sets(row):
    try:
        raw_score = row['Uitslag'] # "3-1 25-14..."
        main_score = raw_score.split(' ')[0] # "3-1"
        
        home_sets = int(main_score.split('-')[0])
        away_sets = int(main_score.split('-')[1])
        
        if row['Thuis'] == selected_team:
            return home_sets - away_sets # +3 or -1 etc.
        else:
            return away_sets - home_sets
    except:
        return 0

# Apply the new logic
my_matches['Net_Sets'] = my_matches.apply(get_net_sets, axis=1)
my_matches['Team Performance (Cumulative)'] = my_matches['Net_Sets'].cumsum()

# Plotting with a baseline
st.line_chart(my_matches, x='Datum', y='Team Performance (Cumulative)')

# Add a zero line explanation
st.caption("📈 Rising Line = Winning more sets than losing. 📉 Falling Line = Losing more sets.")