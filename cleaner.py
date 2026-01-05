import pandas as pd

# 1. Load the raw data
df = pd.read_csv("data/volleyball_raw.csv")

print("Raw rows:", len(df))

# 2. Drop rows where there is no result yet (Future matches)
# Matches that haven't happened usually have NaN (empty) in 'Uitslag'
df = df.dropna(subset=['Uitslag'])

# 3. The Function to clean the "Uitslag" column
def parse_score(score_string):
    try:
        # Example: "3-0 25-21, 25-21, 26-24"
        
        # Split into [Result, Details] -> ["3-0", "25-21, 25-21..."]
        parts = score_string.split(' ', 1) 
        match_result = parts[0] # "3-0"
        
        # Split "3-0" into Home and Away
        sets = match_result.split('-')
        home_sets = int(sets[0])
        away_sets = int(sets[1])
        
        return pd.Series([home_sets, away_sets])
    except:
        return pd.Series([0, 0])

# 4. Apply the function
# This creates two new columns instantly
df[['Sets_Home', 'Sets_Away']] = df['Uitslag'].apply(parse_score)

# 5. Calculate Points (The Business Logic)
# Usually: 4-0 = 5pts, 3-2 = 3pts, etc. 
# Or is it simple: 1 set = 1 point?
# Based on your league: Usually 1 set won = 1 point in Dutch recreational leagues.
df['Points_Home'] = df['Sets_Home']
df['Points_Away'] = df['Sets_Away']

# Show the clean data
print(df[['Thuis', 'Gast', 'Sets_Home', 'Sets_Away']].head())

# Save the clean version
df.to_csv("data/volleyball_clean.csv", index=False)
print("Saved clean data!")