import os

# Define the files we want to remove
files_to_delete = [
    "data/volleyball_raw.csv",
    "data/volleyball_clean.csv",
    "data/league_standings.csv",
    "output/standings_chart.png"
]

print("🧹 CLEANUP INITIATED...")

for file_path in files_to_delete:
    # Check if file exists before trying to delete
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"✅ Deleted: {file_path}")
        except Exception as e:
            print(f"❌ Error deleting {file_path}: {e}")
    else:
        print(f"⚠️  Skipped (Not found): {file_path}")

print("✨ Cleanup Complete. Ready for a fresh run.")