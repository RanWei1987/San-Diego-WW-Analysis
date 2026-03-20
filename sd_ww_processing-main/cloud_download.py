import sys
import os
from pathlib import Path

if len(sys.argv) < 4:
    print("Usage: python cloud_download.py <table_filename> <dump_folder> <target_column1> <target_column2> ... <target_columnN>")
    sys.exit(1)

table_file = sys.argv[1]
dump_dir = sys.argv[2]
target_columns = sys.argv[3:]

# Ensure dump folder exists
if os.path.exists(dump_dir) and os.path.isdir(dump_dir):
    print("Folder exists")
    folder = Path(dump_dir)
    for f in folder.iterdir():
        if f.is_file():
            f.unlink() 
else:
    os.makedirs(dump_dir)

import pandas as pd
data = pd.read_csv(table_file, delimiter="\t", keep_default_na=False)

def download_file(gs_path, dump_folder, max_retries=5):
    file_name = os.path.basename(gs_path)
    for attempt in range(1, max_retries + 1):
        print(f"Downloading {file_name}, attempt {attempt}...")
        ret = os.system(f'gcloud storage cp "{gs_path}" "{dump_folder}"')
        if ret == 0:
            print(f"{file_name} downloaded successfully.")
            break
        elif attempt == max_retries:
            raise RuntimeError(f"All attempts to download {file_name} failed.")

# Loop through table
for idx, row in data.iterrows():
    for column in target_columns:
        gs_file = row[column]
        if gs_file != "":
            download_file(gs_file, dump_dir)
