import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def load_accounts():
    df = pd.read_excel(DATA_DIR / "accounts.xlsx", engine='openpyxl')
    return df[df["status"] == "active"].to_dict(orient="records")
