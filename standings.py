import pandas as pd

# 1. Load the clean data
df = pd.read_csv("volleyball_clean.csv")

# 2. Calculate points earned at Home
home_standings = df.groupby('Thuis')['Points_Home'].sum().reset_index()
home_standings.columns = ['Team', 'Points']

# 3. Calculate points earned Away
away_standings = df.groupby('Gast')['Points_Away'].sum().reset_index()
away_standings.columns = ['Team', 'Points']

# 4. Merge them (Union)
total_standings = pd.concat([home_standings, away_standings])

# 5. Sum it all up by Team
final_table = total_standings.groupby('Team')['Points'].sum().reset_index()

# 6. Sort it (Highest points first)
final_table = final_table.sort_values(by='Points', ascending=False)

# 7. Add a Rank column (1, 2, 3...)
final_table['Rank'] = range(1, len(final_table) + 1)

# Display the League Table
print("--- LEAGUE STANDINGS ---")
print(final_table[['Rank', 'Team', 'Points']].to_string(index=False))

# Save it to send to your captain later
final_table.to_csv("league_standings.csv", index=False)