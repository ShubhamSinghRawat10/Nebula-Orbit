"""Idempotently import the supplied CSV files into the configured MongoDB."""
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

from data_loader import import_curriculum, import_interaction_history

load_dotenv()

ROOT = Path(__file__).resolve().parent
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/"), serverSelectionTimeoutMS=3000)
db = client[os.getenv("MONGODB_DB", "nebula")]

curriculum = import_curriculum(db, ROOT)
print("Curriculum imported:", curriculum)

salt = os.getenv("DATASET_HASH_SALT", "")
if salt:
    interactions = import_interaction_history(db, ROOT, salt)
    print(f"Assessment history imported: {interactions} rows (names omitted, student IDs pseudonymized).")
else:
    print("Assessment rows were not imported. Set DATASET_HASH_SALT (24+ characters) to import them safely.")
