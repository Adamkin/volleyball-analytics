import os
import time

def run_step(script_name, description):
    print(f"\n--- 🚀 STARTING: {description} ({script_name}) ---")
    exit_code = os.system(f"python {script_name}")
    if exit_code == 0:
        print(f"✅ SUCCESS: {description} complete.")
        time.sleep(0.5)
    else:
        print(f"❌ FAILURE: {description} crashed.")
        exit()

def main():
    print("🏐 VOLLEYBALL PIPELINE INITIATED 🏐")
    print("=======================================")

    # 1. Ask for Cleanup
    user_input = input("Do you want to clear old data first? (y/n): ").lower()
    if user_input == 'y':
        run_step("cleanup.py", "Cleaning Old Files")
    else:
        print("Skipping cleanup. Appending to existing/new run.")

    # 2. Run the Pipeline
    run_step("scraper.py", "Scraping Nuvoc Website")
    run_step("cleaner.py", "Parsing Scores")
    run_step("standings.py", "Calculating Stats")
    run_step("visualise.py", "Generating Report")
    run_step("prediction.py", "Running Match Predictor")
    
    print("\n=======================================")
    
    print("\n=======================================")
    print("✨ DONE. Check 'output/standings_table.png' ✨")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()  