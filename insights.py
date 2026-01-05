import pandas as pd
import matplotlib.pyplot as plt
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. Load Data
df = pd.read_csv("data/volleyball_clean.csv")

MY_TEAM = "ABC Volleybal 3" 

print(f"\n--- 📊 {MY_TEAM.upper()} ANALYTICS ---")

# --- DATA PREP ---
home_stats = df.groupby('Thuis')[['Small_Pts_Home', 'Small_Pts_Away']].sum()
away_stats = df.groupby('Gast')[['Small_Pts_Away', 'Small_Pts_Home']].sum()

home_stats.columns = ['Scored', 'Conceded']
away_stats.columns = ['Scored', 'Conceded']

total_stats = home_stats.add(away_stats, fill_value=0)

# --- VISUALISATION ---
plt.figure(figsize=(10, 8))

# 1. Plot Competitors (Gray)
plt.scatter(total_stats['Conceded'], total_stats['Scored'], 
            color='#bdc3c7', s=100, alpha=0.6, label='Competitors')

# 2. Plot YOUR Team (Red)
if MY_TEAM in total_stats.index:
    my_team_stats = total_stats.loc[MY_TEAM]
    
    # The Dot
    plt.scatter(my_team_stats['Conceded'], my_team_stats['Scored'], 
                color='#e74c3c', s=250, zorder=10, label=MY_TEAM)
    
    # The Ring
    plt.scatter(my_team_stats['Conceded'], my_team_stats['Scored'], 
                facecolors='none', edgecolors='black', linewidth=2, s=250, zorder=11)
    
# The Label (Tighter fit)
    # Changed from (-5, +10) to (-2, +4)
    plt.text(my_team_stats['Conceded'] - 2, my_team_stats['Scored'] + 4, 
             MY_TEAM, fontsize=11, fontweight='bold', color='#c0392b', zorder=12)

# 3. Plot Other Labels
for team, row in total_stats.iterrows():
    if team != MY_TEAM:
        # Standard offset for others
        plt.text(row['Conceded'] + 2, row['Scored'], team, fontsize=8, alpha=0.7)

# 4. Average Lines (The Crosshair)
avg_scored = total_stats['Scored'].mean()
avg_conceded = total_stats['Conceded'].mean()

plt.axhline(avg_scored, color='green', linestyle='--', alpha=0.3, label="Avg Offense") 
plt.axvline(avg_conceded, color='blue', linestyle='--', alpha=0.3, label="Avg Defense") 

# 5. Titles and Axis
plt.title(f"League Matrix: {MY_TEAM}", fontsize=14, weight='bold')
plt.xlabel("Points Conceded (Right is Better →)", fontsize=11)
plt.ylabel("Points Scored (↑ Top is Better)", fontsize=11)
plt.grid(True, linestyle=':', alpha=0.4)

# 6. Invert X-Axis (So Low Conceded is on the Right)
plt.gca().invert_xaxis()

plt.legend(loc='lower left')
plt.tight_layout()
plt.savefig("output/offense_vs_defense.png")
print(f"📈 Insight Generated.")
plt.show()