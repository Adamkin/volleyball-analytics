import pandas as pd
import requests
import os

# --- CONFIGURATION ---
URL = "https://www.nuvoc.nl/main/cgi-bin/volley_results.cgi?entry=speeldata&poule=2B&competie=ndrc25&"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
DATA_DIR = "data"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def update_files():
    print(f"📡 Connecting to {URL}...")
    try:
        r = requests.get(URL, headers=HEADERS)
        
        # 1. SCRAPE RAW SCHEDULE
        # Look for table with "Thuis" (Home Team)
        tables = pd.read_html(r.text, match="Thuis")
        
        if len(tables) == 0:
            print("❌ No match table found!")
            return
            
        raw_df = tables[0]
        raw_df.to_csv(f"{DATA_DIR}/volleyball_raw.csv", index=False)
        print("✅ Saved 'volleyball_raw.csv'")

        # 2. PROCESS INTO 'CLEAN' DATA (For Moneyball Chart)
        print("⚙️ Processing match data...")
        
        clean_rows = []
        
        for _, row in raw_df.iterrows():
            try:
                # Check if match is played (has a score like "3-1")
                if pd.isna(row['Uitslag']):
                    continue
                    
                score_str = str(row['Uitslag'])
                if "-" not in score_str:
                    continue

                # Parse "3-1 25-10, 25-20..."
                parts = score_str.split(' ')
                main_score = parts[0] # "3-1"
                set_scores = " ".join(parts[1:]) # "25-10, 25-20..."
                
                # Sets
                sets_home = int(main_score.split('-')[0])
                sets_away = int(main_score.split('-')[1])
                
                # Small Points (Summing the 25-10, 25-20 part)
                home_pts = 0
                away_pts = 0
                
                # Simple parser for points 25-10, 25-12 etc
                # Removing commas and splitting by space might be needed depending on format
                # Assuming format "25-10, 25-12"
                clean_sets = set_scores.replace(',', '').split(' ')
                for s in clean_sets:
                    if '-' in s:
                        p_h, p_a = s.split('-')
                        if p_h.isdigit() and p_a.isdigit():
                            home_pts += int(p_h)
                            away_pts += int(p_a)
                
                clean_rows.append({
                    'Datum': row['Datum'],
                    'Thuis': row['Thuis'],
                    'Gast': row['Gast'],
                    'Sets_Home': sets_home,
                    'Sets_Away': sets_away,
                    'Small_Pts_Home': home_pts,
                    'Small_Pts_Away': away_pts
                })
            except Exception as e:
                # Skip bad rows silently
                continue
                
        clean_df = pd.DataFrame(clean_rows)
        clean_df.to_csv(f"{DATA_DIR}/volleyball_clean.csv", index=False)
        print("✅ Saved 'volleyball_clean.csv'")

        # 3. RECALCULATE STANDINGS (For Rank & Table)
        print("🏆 Updating League Standings...")
        
        # Get list of all unique teams
        teams = pd.concat([raw_df['Thuis'], raw_df['Gast']]).unique()
        standings_data = []
        
        for team in teams:
            if pd.isna(team): continue
            
            # Filter matches for this team
            home_games = clean_df[clean_df['Thuis'] == team]
            away_games = clean_df[clean_df['Gast'] == team]
            
            played = len(home_games) + len(away_games)
            
            # Calculate League Points (Assuming 1 Set Won = 1 Point)
            # You can adjust this math if your league has different rules
            points = home_games['Sets_Home'].sum() + away_games['Sets_Away'].sum()
            
            sets_won = points # Same as points in this logic
            sets_lost = home_games['Sets_Away'].sum() + away_games['Sets_Home'].sum()
            
            scored = home_games['Small_Pts_Home'].sum() + away_games['Small_Pts_Away'].sum()
            conceded = home_games['Small_Pts_Away'].sum() + away_games['Small_Pts_Home'].sum()
            
            ppm = points / played if played > 0 else 0
            
            standings_data.append({
                'Team': team,
                'League_Pts': points,
                'Played': played,
                'Scored': sets_won,   # Using Sets for Scored/Conceded column in CSV standard
                'Conceded': sets_lost,
                'Delta': scored - conceded,
                'PPM': ppm
            })
            
        standings_df = pd.DataFrame(standings_data)
        
        # Sort by Points (Desc), then Delta (Desc)
        standings_df = standings_df.sort_values(by=['League_Pts', 'Delta'], ascending=[False, False])
        
        # Add Rank
        standings_df['Rank'] = range(1, len(standings_df) + 1)
        
        standings_df.to_csv(f"{DATA_DIR}/league_standings.csv", index=False)
        print("✅ Saved 'league_standings.csv'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise e

if __name__ == "__main__":
    update_files()