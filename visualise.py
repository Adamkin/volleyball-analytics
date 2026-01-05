import pandas as pd
import matplotlib.pyplot as plt
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

df = pd.read_csv("data/league_standings.csv")

# Setup Plot
fig, ax = plt.subplots(figsize=(10, 6)) # Made it slightly wider
ax.axis('tight')
ax.axis('off')

# Data Selection (Added Delta)
table_data = df[['Rank', 'Team', 'League_Pts', 'Played', 'PPM', 'Delta']]
col_labels = ['#', 'Team', 'Pts', 'Gms', 'Avg', 'Delta']

# Draw Table
the_table = ax.table(cellText=table_data.values,
                     colLabels=col_labels,
                     loc='center',
                     cellLoc='center',
                     colWidths=[0.05, 0.35, 0.1, 0.1, 0.1, 0.1]) # Adjust column widths

# Styling
the_table.auto_set_font_size(False)
the_table.set_fontsize(11)
the_table.scale(1.2, 1.8)

for (row, col), cell in the_table.get_celld().items():
    if row == 0:
        cell.set_facecolor('#40466e')
        cell.set_text_props(color='white', weight='bold')
    elif row % 2 == 0:
        cell.set_facecolor('#f2f2f2')

# Highlight the Delta column (Column index 5)
    if col == 5 and row > 0:
        val = int(table_data.iloc[row-1]['Delta'])
        if val > 0:
            cell.set_text_props(color='green', weight='bold')
        elif val < 0:
            cell.set_text_props(color='#D22B2B') # Red

plt.title("NDRC League Standings 2026", fontsize=16, weight='bold', pad=20)
plt.savefig("output/standings_table.png", bbox_inches='tight', dpi=300)
print("✅ Table saved with Delta column!")