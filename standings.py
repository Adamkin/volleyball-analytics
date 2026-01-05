import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

df = pd.read_csv("data/volleyball_clean.csv")

# 1. Home Stats: (Points, Games, Scored, Conceded)
home = df.groupby('Thuis').agg(
    League_Pts=('Points_Home', 'sum'),
    Played=('Thuis', 'count'),
    Scored=('Small_Pts_Home', 'sum'),
    Conceded=('Small_Pts_Away', 'sum')
).reset_index().rename(columns={'Thuis': 'Team'})

# 2. Away Stats
away = df.groupby('Gast').agg(
    League_Pts=('Points_Away', 'sum'),
    Played=('Gast', 'count'),
    Scored=('Small_Pts_Away', 'sum'),
    Conceded=('Small_Pts_Home', 'sum')
).reset_index().rename(columns={'Gast': 'Team'})

# 3. Merge & Sum
total = pd.concat([home, away]).groupby('Team').sum().reset_index()

# 4. Calculate The "Delta"
total['Delta'] = total['Scored'] - total['Conceded']
total['PPM'] = (total['League_Pts'] / total['Played']).round(2)

# 5. Sort by League Points first, then Delta (Tie Breaker)
total = total.sort_values(by=['League_Pts', 'Delta'], ascending=[False, False])
total['Rank'] = range(1, len(total) + 1)

# Save
total.to_csv("data/league_standings.csv", index=False)
print("✅ Standings Calculated (including Point Delta).")