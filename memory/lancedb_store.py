import lancedb
from config import settings
import json
import os

os.makedirs(os.path.dirname(settings.LANCEDB_URI), exist_ok=True)
db = lancedb.connect(settings.LANCEDB_URI)

# Ensure the tables exist for long-term vector embeddings
if "routes" not in db.table_names():
    db.create_table("routes", data=[{"vector": [0.0]*384, "name": "init", "phrase": "init"}], mode="overwrite")

def save_directive_to_disk(directive: dict, filename: str):
    os.makedirs(settings.DIRECTIVES_DIR, exist_ok=True)
    filepath = os.path.join(settings.DIRECTIVES_DIR, f"{filename}.json")
    with open(filepath, "w") as f:
        json.dump(directive, f, indent=4)
    return filepath
