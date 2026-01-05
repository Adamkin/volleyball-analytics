import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. Load Data
df = pd.read_csv("data/volleyball_raw.csv")
df = df.dropna(subset=['Uitslag'])

# 2. The Advanced Parser
def parse_full_stats(score_string):
    try:
        # Input: "3-0 25-21, 25-21, 26-24"
        
        # separate "3-0" from the rest
        parts = score_string.split(' ', 1)
        match_result = parts[0] # "3-0"
        
        # Parse Sets (3 vs 0)
        sets = match_result.split('-')
        sets_h = int(sets[0])
        sets_a = int(sets[1])
        
        # Parse Small Points (76 vs 66)
        points_h = 0
        points_a = 0
        
        if len(parts) > 1:
            # We have set scores: "25-21, 25-21, 26-24"
            raw_scores = parts[1].split(',')
            for s in raw_scores:
                s = s.strip() # Remove spaces
                if '-' in s:
                    p = s.split('-')
                    points_h += int(p[0])
                    points_a += int(p[1])
        
        return pd.Series([sets_h, sets_a, points_h, points_a])
    except:
        return pd.Series([0, 0, 0, 0])

# 3. Apply the function
df[['Sets_Home', 'Sets_Away', 'Small_Pts_Home', 'Small_Pts_Away']] = df['Uitslag'].apply(parse_full_stats)

# 4. Calculate League Points (1 set = 1 point logic)
df['Points_Home'] = df['Sets_Home']
df['Points_Away'] = df['Sets_Away']

# Save
df.to_csv("data/volleyball_clean.csv", index=False)
print("✅ Data Cleaned: Extracted Sets AND Small Points.")