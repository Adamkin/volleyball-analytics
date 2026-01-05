import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

MY_TEAM = "ABC Volleybal 3" 

print(f"\n--- 🔮 PREDICTION ENGINE: {MY_TEAM} ---")

# 1. Load Data
schedule = pd.read_csv("data/volleyball_raw.csv")
standings = pd.read_csv("data/league_standings.csv")

# 2. Find Next Match
future_matches = schedule[
    ((schedule['Thuis'] == MY_TEAM) | (schedule['Gast'] == MY_TEAM)) & 
    (schedule['Uitslag'].isna())
]

if len(future_matches) == 0:
    print("No upcoming matches found!")
    exit()

next_match = future_matches.iloc[0]

# Identify Context
if next_match['Thuis'] == MY_TEAM:
    opponent = next_match['Gast']
    location = "🏠 HOME"
else:
    opponent = next_match['Thuis']
    location = "🚌 AWAY"

print(f"\n📅 NEXT MATCH: {next_match['Datum']}")
print(f"🆚 Opponent:   {opponent}")
print(f"📍 Location:   {location}")

# --- NEW FEATURE: HEAD-TO-HEAD HISTORY ---
# Check if we played them before
h2h = schedule[
    ((schedule['Thuis'] == MY_TEAM) & (schedule['Gast'] == opponent)) |
    ((schedule['Gast'] == MY_TEAM) & (schedule['Thuis'] == opponent))
]

# Filter for games that actually have a result
past_h2h = h2h[h2h['Uitslag'].notna()]

print("\n📜 HISTORY:")
if len(past_h2h) > 0:
    last_game = past_h2h.iloc[0]
    print(f"   Last meeting: {last_game['Uitslag'].split(' ')[0]} (Sets)")
    # Did we win?
    # Simple check: parse the string "3-1"
    res = last_game['Uitslag'].split(' ')[0]
    sets = res.split('-')
    
    # We need to know who was Home in that past game to know if "3" is us or them
    if last_game['Thuis'] == MY_TEAM:
        we_won_sets = int(sets[0])
        they_won_sets = int(sets[1])
    else:
        we_won_sets = int(sets[1])
        they_won_sets = int(sets[0])
        
    if we_won_sets > they_won_sets:
        print("   Result: You WON that game. ✅")
    else:
        print("   Result: You LOST that game. ❌")
else:
    print("   First time meeting this season.")

# --- STATISTICAL PREDICTION ---
def get_team_ppm(team_name):
    try:
        row = standings[standings['Team'] == team_name].iloc[0]
        return row['PPM']
    except:
        return 2.0

my_ppm = get_team_ppm(MY_TEAM)
opp_ppm = get_team_ppm(opponent)

print(f"\n📊 FORM GUIDE (Points Per Match):")
print(f"   You:  {my_ppm} ppm")
print(f"   They: {opp_ppm} ppm")

# Calculate Delta
ppm_diff = my_ppm - opp_ppm

# --- SCORE PREDICTOR LOGIC ---
# Based on typical volleyball spreads
# Logic: Matches are exactly 3 sets. Max score 3-0.
predicted_score = "???"

# We use the Form Difference to guess the split
if ppm_diff > 0.8:
    predicted_score = "3-0 (Dominant Win)"
elif ppm_diff > 0.1:
    predicted_score = "2-1 (Close Win)"
elif ppm_diff > -0.8:
    predicted_score = "1-2 (Close Loss)"
else:
    predicted_score = "0-3 (Clear Loss)"

print(f"\n🧠 ALGORITHM PREDICTION:")
print(f"   Projected Score: {predicted_score}")

# Probability Bar
total_strength = my_ppm + opp_ppm
win_prob = (my_ppm / total_strength) * 100
bar_length = 20
filled_length = int(bar_length * win_prob // 100)
bar = '█' * filled_length + '▒' * (bar_length - filled_length) # Used ▒ for empty
print(f"   Win Probability: {win_prob:.1f}%")
print(f"   |{bar}|")