import os
import shutil

folders_to_scrub = ["data", "output"]

print("🧹 NUCLEAR CLEANUP INITIATED...")

for folder in folders_to_scrub:
    # Check if folder exists
    if os.path.exists(folder):
        # List all files in the folder
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                # If it's a file, delete it
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    print(f"✅ Deleted: {filename}")
                # If it's a subfolder, remove it tree and all
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"✅ Deleted folder: {filename}")
            except Exception as e:
                print(f"❌ Failed to delete {file_path}. Reason: {e}")
    else:
        print(f"⚠️  Folder '{folder}' does not exist yet.")

print("✨ All folders are empty and ready.")