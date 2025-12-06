"""
data_cleaning.py

Purpose:
Clean messy sales data and output a cleaned CSV file.
"""

import pandas as pd

# FUNCTION: load_data
# Purpose: load a CSV file into a pandas DataFrame
# Requirements:
# - accept a file path as a string
# - read the CSV
# - drop rows that are completely empty
# - return the DataFrame
def load_data(file_path: str):

path = str(Path(path))

# Detect encoding (try common encodings)
encoding = None
with open(path, "rb") as f:
    raw = f.read(8192)
for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
    try:
        raw.decode(enc)
        encoding = enc
        break
    except Exception:
        continue
if encoding is None:
    encoding = "utf-8"

# Sniff delimiter from a sample
sample = raw.decode(encoding, errors="ignore")
try:
    dialect = csv.Sniffer().sniff(sample)
    sep = dialect.delimiter
except Exception:
    sep = ","

# Read CSV
df = pd.read_csv(path, sep=sep, encoding=encoding, skipinitialspace=True, low_memory=False)

# Normalize column names: strip, lowercase, replace non-alphanum with underscore
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r"[^0-9a-z]+", "_", regex=True)
    .str.strip("_")
)

# Strip whitespace from object columns
obj_cols = df.select_dtypes(include=["object"]).columns
for c in obj_cols:
    df[c] = df[c].astype(str).str.strip().replace({"nan": pd.NA})

# Normalize common missing tokens to NA
df.replace(["", "NA", "N/A", "na", "n/a", "none", "None", "NULL", "null", "nan"], pd.NA, inplace=True)

# Convert currency/number-like strings to numeric where appropriate
for c in df.select_dtypes(include=["object"]).columns:
    # Remove common currency symbols and whitespace, then thousands separators
    cleaned = (
        df[c]
        .astype(str)
        .str.replace(r"[\$\€\£]", "", regex=True)
        .str.replace(r"\s+", "", regex=True)
        .str.replace(",", "", regex=True)
    )
    # If a majority of values are numeric after cleaning, convert
    is_numeric_like = cleaned.str.match(r"^-?\d+(\.\d+)?$") & ~cleaned.isin(["nan", "None", "NoneType"])
    if cleaned.size > 0 and is_numeric_like.sum() / cleaned.size >= 0.5:
        df[c] = pd.to_numeric(cleaned.replace({"nan": pd.NA, "None": pd.NA}), errors="coerce")

# Parse date/time columns heuristically (column name contains 'date' or 'time')
date_cols = [c for c in df.columns if "date" in c or "time" in c]
for c in date_cols:
    df[c] = pd.to_datetime(df[c], errors="coerce", infer_datetime_format=True)

# Drop exact duplicates and reset index
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)

return df
print(f"Loaded {data.shape[0]} rows")


# FUNCTION: clean_column_names
# Purpose: standardize column names
# Requirements:
# - make all column names lowercase
# - replace spaces with underscores
# - remove extra whitespace
# - return cleaned DataFrame
def clean_column_names(df):

  path = str(Path(path))

# Read a sample of the file as bytes for sniffing
with open(path, "rb") as f:
    sample_bytes = f.read(32_768)

# Detect encoding by trying common encodings
encoding = None
for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
    try:
        sample_bytes.decode(enc)
        encoding = enc
        break
    except Exception:
        continue
if encoding is None:
    encoding = "utf-8"

sample_text = sample_bytes.decode(encoding, errors="ignore")

# Sniff delimiter using csv.Sniffer, fallback to common guess
try:
    dialect = csv.Sniffer().sniff(sample_text)
    sep = dialect.delimiter
except Exception:
    # prefer semicolon if appears more often than comma, otherwise comma
    if sample_text.count(";") > sample_text.count(","):
        sep = ";"
    else:
        sep = ","

# Read CSV with guessed settings
df = pd.read_csv(path, sep=sep, encoding=encoding, skipinitialspace=True, low_memory=False)

# Normalize column names: trim, lowercase, non-alnum -> underscore
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r"[^0-9a-z]+", "_", regex=True)
    .str.strip("_")
)

# Normalize common missing tokens to pd.NA
na_tokens = ["", " ", "-", "na", "n/a", "none", "null", "nan", "NA", "N/A", "None", "NULL"]
df.replace(na_tokens, pd.NA, inplace=True)

# Strip whitespace from object columns and convert obvious textual 'nan'/'None' to NA
obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
for c in obj_cols:
    df[c] = df[c].astype(str).str.strip()
    df.loc[df[c].isin(["", "nan", "None", "NoneType"]), c] = pd.NA

# Heuristic numeric conversion for string columns
for c in obj_cols:
    col = df[c].astype("string")
    # Remove currency symbols, thousands separators, and internal spaces
    cleaned = col.str.replace(r"[\$\€\£]", "", regex=True).str.replace(r"[,\s]", "", regex=True)
    # Count non-empty values and numeric-like values
    non_null = cleaned.dropna()
    if len(non_null) == 0:
        continue
    numeric_like = non_null.str.match(r"^-?\d+(\.\d+)?$")
    # If a strong majority are numeric-like, convert column
    if numeric_like.sum() / len(non_null) >= 0.6:
        df[c] = pd.to_numeric(cleaned.replace({"nan": pd.NA, "None": pd.NA}), errors="coerce")

# Heuristic date/time parsing: columns containing date/time-related keywords
date_keywords = ("date", "time", "timestamp", "day")
date_cols = [c for c in df.columns if any(k in c for k in date_keywords)]
for c in date_cols:
    df[c] = pd.to_datetime(df[c], errors="coerce", infer_datetime_format=True)

# Final cleanup: drop exact duplicates and reset 
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)

return df

# FUNCTION: handle_missing_values
# Purpose: handle missing prices and quantities consistently
# Requirements:
# - convert price and quantity to numeric
# - fill or drop missing values in a consistent way
# - return cleaned DataFrame
def handle_missing_values(df):

df = df.copy()

# percent missing per column
missing_pct = df.isna().mean()

# drop columns with too many missing values
col_drop_threshold = 0.60
cols_to_drop = missing_pct[missing_pct > col_drop_threshold].index.tolist()
if cols_to_drop:
    df.drop(columns=cols_to_drop, inplace=True)

# drop rows with too many missing values
row_drop_threshold = 0.50
rows_to_drop = df.isna().mean(axis=1) > row_drop_threshold
if rows_to_drop.any():
    df = df.loc[~rows_to_drop].copy()

# Impute remaining columns by dtype
for col in df.columns:
    ser = df[col]
    # skip if no missing values
    if not ser.isna().any():
        continue

    # Numeric types
    if ptypes.is_numeric_dtype(ser):
        med = ser.median(skipna=True)
        # fallback if median is NaN (all null): use 0
        fill_val = med if pd.notna(med) else 0
        df[col] = ser.fillna(fill_val)

    # Datetime types
    elif ptypes.is_datetime64_any_dtype(ser):
        # try to fill with mode (most common timestamp), otherwise leave as NaT
        try:
            mode_vals = ser.dropna().mode()
            if not mode_vals.empty:
                df[col] = ser.fillna(mode_vals.iloc[0])
            else:
                df[col] = ser  # leave as-is (NaT)
        except Exception:
            df[col] = ser

    # Boolean types
    elif ptypes.is_bool_dtype(ser):
        try:
            mode_vals = ser.dropna().mode()
            fill_val = bool(mode_vals.iloc[0]) if not mode_vals.empty else False
        except Exception:
            fill_val = False
        df[col] = ser.fillna(fill_val)

    # Categorical / object / string types
    else:
        # if categorical, preserve categories when possible
        try:
            mode_vals = ser.dropna().mode()
            if not mode_vals.empty:
                fill_val = mode_vals.iloc[0]
            else:
                fill_val = "missing"
        except Exception:
            fill_val = "missing"
        df[col] = ser.fillna(fill_val)

# reset index after row drops
df.reset_index(drop=True, inplace=True)
return df

# FUNCTION: remove_invalid_rows
# Purpose: remove rows with invalid numeric values
# Requirements:
# - remove rows with negative price
# - remove rows with negative quantity
# - return DataFrame
def remove_invalid_rows(df):

def remove_invalid_rows(df):
    """
    Remove obviously invalid rows from a sales DataFrame (works on a copy).
    Heuristics used:
    - Drop rows that are entirely empty.
    - Drop rows missing all "id"-like columns (order_id, id, transaction_id, invoice_id, ...).
    - Drop rows where all numeric columns are missing.
    - Drop rows with negative values in money/amount columns.
    - Drop rows with non-positive quantities (quantity/qty/units).
    - Drop rows missing all date/time columns (if present).
    Returns a cleaned DataFrame (index reset).
    """
    import pandas as pd
    from pandas.api import types as ptypes

    df = df.copy()

    # 1) Drop rows that are entirely empty
    df = df.dropna(how="all")
    if df.empty:
        return df.reset_index(drop=True)

    # 2) Drop rows missing all id-like columns
    id_candidates = {"order_id", "order", "id", "transaction_id", "invoice_id", "sale_id", "sales_id"}
    id_cols = [c for c in df.columns if c.lower() in id_candidates]
    if id_cols:
        df = df.dropna(subset=id_cols, how="all")
        if df.empty:
            return df.reset_index(drop=True)

    # 3) Drop rows where all numeric columns are missing (if any numeric cols exist)
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        df = df.dropna(subset=numeric_cols, how="all")
        if df.empty:
            return df.reset_index(drop=True)

    # 4) Drop rows with negative values for money-like columns
    money_keywords = ("price", "amount", "total", "revenue", "cost", "subtotal", "unit_price", "sale", "sales")
    for col in df.columns:
        col_l = col.lower()
        if any(k in col_l for k in money_keywords) and ptypes.is_numeric_dtype(df[col]):
            # keep rows where value is NA or >= 0
            df = df[df[col].isna() | (df[col] >= 0)]
            if df.empty:
                return df.reset_index(drop=True)

    # 5) Drop rows with non-positive quantities (quantity should usually be > 0)
    qty_keywords = ("quantity", "qty", "units")
    for col in df.columns:
        col_l = col.lower()
        if any(k in col_l for k in qty_keywords) and ptypes.is_numeric_dtype(df[col]):
            df = df[df[col].isna() | (df[col] > 0)]
            if df.empty:
                return df.reset_index(drop=True)

    # 6) Drop rows missing all date/time columns (if datetime cols exist)
    date_keywords = ("date", "time", "timestamp")
    date_cols = [c for c in df.columns if any(k in c.lower() for k in date_keywords) and ptypes.is_datetime64_any_dtype(df[c])]
    if date_cols:
        df = df.dropna(subset=date_cols, how="all")
        if df.empty:
            return df.reset_index(drop=True)

    # 7) As a final guard, remove rows that have no meaningful data (all remaining values NA or empty strings)
    def _row_has_value(ser):
        # consider non-empty strings and non-null numbers/datetimes as meaningful
        if ptypes.is_object_dtype(ser) or ptypes.is_string_dtype(ser):
            return ser.astype(str).str.strip().replace({"": pd.NA}).notna()
        else:
            return ser.notna()

    meaningful = pd.DataFrame({c: _row_has_value(df[c]) for c in df.columns})
    keep_mask = meaningful.any(axis=1)
    df = df.loc[keep_mask].copy()

    df.reset_index(drop=True, inplace=True)
    return df

if __name__ == "__main__":
    raw_path = "data/raw/sales_data_raw.csv"
    cleaned_path = "data/processed/sales_data_clean.csv"

    df_raw = load_data(raw_path)
    df_clean = clean_column_names(df_raw)
    df_clean = handle_missing_values(df_clean)
    df_clean = remove_invalid_rows(df_clean)

    df_clean.to_csv(cleaned_path, index=False)

    print("Cleaning complete. First few rows:")
    print(df_clean.head())

