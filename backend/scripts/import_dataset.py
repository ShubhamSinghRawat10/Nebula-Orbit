"""Idempotently import the supplied CSV files into the configured MongoDB."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.data_loader import import_curriculum, import_interaction_history

client = MongoClient(os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/"), serverSelectionTimeoutMS=3000)
db = client[os.getenv("MONGODB_DB", "nebula")]

curriculum = import_curriculum(db, ROOT / "data")
print("Curriculum imported:", curriculum)

salt = os.getenv("DATASET_HASH_SALT", "")
if salt:
    interactions = import_interaction_history(db, ROOT / "data", salt)
    print(f"Assessment history imported: {interactions} rows (names omitted, student IDs pseudonymized).")
else:
    print("Assessment rows were not imported. Set DATASET_HASH_SALT (24+ characters) to import them safely.")
