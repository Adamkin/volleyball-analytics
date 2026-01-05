import pandas as pd
import requests

# The exact URL you found
url = "https://www.nuvoc.nl/main/cgi-bin/volley_results.cgi?entry=speeldata&poule=2B&competie=ndrc25&"

# Pretend to be a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    print(f"Connecting to {url}...")
    r = requests.get(url, headers=headers)
    
    # Look for a table that contains the column "Thuis"
    tables = pd.read_html(r.text, match="Thuis")
    
    if len(tables) > 0:
        df = tables[0]
        print("Success! Table found.")
        print(df.head())
        
        # Save it
        df.to_csv("data/volleyball_raw.csv", index=False)
        print("Saved to 'data/volleyball_raw.csv'.")
    else:
        print("Still no table found. The layout might be very tricky.")

except Exception as e:
    print(f"Error: {e}")