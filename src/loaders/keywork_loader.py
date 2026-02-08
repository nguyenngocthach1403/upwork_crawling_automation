import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def load_keywords_for_account(account_id: str):
    df_map = pd.read_excel(DATA_DIR / "account_keyword_map.xlsx", engine='openpyxl')
    df_keywords = pd.read_excel(DATA_DIR / "keywords.xlsx",  engine='openpyxl')

    # keyword_id của account
    keyword_ids = df_map[df_map["account_id"] == account_id]["keyword_id"]

    # join sang keyword
    result = df_keywords[df_keywords["keyword_id"].isin(keyword_ids)]

    return result.to_dict(orient="records")
