import re
import pandas as pd

def extract_phone_number(message):
    pattern = r'91(\d{10,15})'
    match = re.search(pattern, message)
    if match:
        return match.group(1)
    return None

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode("utf-8")

def extract_name(message):
    pattern = r'@⁨([^⁩]+)⁩'
    match = re.search(pattern, message)
    if match:
        return match.group(1).strip()
    return None