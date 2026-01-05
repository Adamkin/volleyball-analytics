import os
import time

def run_step(script_name, description):
    print(f"\n--- 🚀 STARTING: {description} ({script_name}) ---")
    
    # This runs the other python files just like you would in the terminal
    exit_code = os.system(f"python {script_name}")
    
    if exit_code == 0:
        print(f"✅ SUCCESS: {description} complete.")
        time.sleep(1) # Pause for dramatic effect
    else:
        print(f"❌ FAILURE: {description} crashed.")
        exit() # Stop everything if a step fails

def main():
    print("🏐 VOLLEYBALL PIPELINE INITIATED 🏐")
    print("=======================================")
    
    # Step 1: Get the data
    run_step("scraper.py", "Scraping Nuvoc Website")
    
    # Step 2: Clean the data
    run_step("cleaner.py", "Parsing Scores & Logic")
    
    # Step 3: Analyze
    run_step("standings.py", "Calculating League Table")
    
    # Step 4: Visualize
    run_step("visualise.py", "Generating Graphs")
    
    print("\n=======================================")
    print("✨ PIPELINE FINISHED. CHECK 'standings_chart.png' ✨")

if __name__ == "__main__":
    # Force python to work in the right directory (Fixes your path issue)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()