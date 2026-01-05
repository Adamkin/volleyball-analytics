import pandas as pd
import matplotlib.pyplot as plt
import os

# Set folder correctly again
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. Load the standings
df = pd.read_csv("league_standings.csv")

# 2. Create the Bar Chart
plt.figure(figsize=(10, 6)) # Size of the window
bars = plt.barh(df['Team'], df['Points'], color='#50fa7b') # Dracula Green color

# 3. Make it pretty
plt.xlabel('Points')
plt.title('League Standings 2026')
plt.gca().invert_yaxis() # Put #1 at the top, not bottom
plt.grid(axis='x', linestyle='--', alpha=0.7)

# 4. Add the numbers on the bars
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
             f'{int(width)}', va='center')

# 5. Show it (and save it)
plt.tight_layout()
plt.savefig("standings_chart.png") # Saves an image file
print("Chart saved as 'standings_chart.png'!")
plt.show() # Pops up a window