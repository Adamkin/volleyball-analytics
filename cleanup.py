import os

files_to_delete = [
    "data/volleyball_raw.csv",
    "data/volleyball_clean.csv",
    "data/league_standings.csv",
    "output/standings_table.png"  # <--- CHANGED THIS LINE
]

print("🧹 CLEANUP INITIATED...")

for file_path in files_to_delete:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"✅ Deleted: {file_path}")
        except Exception as e:
            print(f"❌ Error deleting {file_path}: {e}")
    else:
        print(f"⚠️  Skipped (Not found): {file_path}")

print("✨ Cleanup Complete.")