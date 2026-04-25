import pandas as pd
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import re
import time

root_dir = Path("matchdata_split")
output_file = "csgo_full_dataset.parquet"

writer = None

files_processed = 0
start_time = time.time()

for match_folder in root_dir.iterdir():

    if not match_folder.is_dir():
        continue

    parts = match_folder.name.rsplit("-", 1)

    if len(parts) == 2:
        match_name, map_name = parts
    else:
        match_name = match_folder.name
        map_name = "unknown"

    print(f"\nMatch: {match_name} | Map: {map_name}")

    for round_folder in match_folder.iterdir():

        if not round_folder.is_dir():
            continue

        round_match = re.search(r'\d+', round_folder.name)

        if not round_match:
            continue

        round_number = int(round_match.group())

        for parquet_file in round_folder.glob("*.parquet"):

            try:

                player_match = re.search(r'Player-(\d+)', parquet_file.stem)
                player_id = int(player_match.group(1)) if player_match else -1

                df = pd.read_parquet(parquet_file, engine="pyarrow")

                df["match"] = match_name
                df["map"] = map_name
                df["round"] = round_number
                df["player"] = player_id

                table = pa.Table.from_pandas(df)

                if writer is None:
                    writer = pq.ParquetWriter(output_file, table.schema)

                writer.write_table(table)

                files_processed += 1

                if files_processed % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"{files_processed} arquivos processados | {elapsed:.1f}s")

            except Exception as e:
                print(f"Erro: {parquet_file} -> {e}")

if writer:
    writer.close()

elapsed = time.time() - start_time

print("\nFinalizado")
print("Arquivos processados:", files_processed)
print("Tempo total:", round(elapsed,2),"s")