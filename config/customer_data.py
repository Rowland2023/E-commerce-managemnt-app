import os
import pandas as pd
from sqlalchemy import create_engine

# 1. Load CSV
df = pd.read_csv("customer.csv")
print("Preview of data:")
print(df.head())

# 2. Normalize phone numbers first (remove spaces and dashes)
df["phone_number"] = (
    df["phone_number"]
    .astype(str)  # ensure it's string
    .str.replace(" ", "", regex=False)
    .str.replace("-", "", regex=False)
)

# 3. Simple validations
assert df["user_id"].notnull().all(), "Null IDs found"
assert df["user_id"].is_unique, "Duplicate IDs found"
assert df["email"].str.contains(r"[^@]+@[^@]+\.[^@]+", regex=True).all(), "Invalid emails found"
assert df["phone_number"].str.contains(r"^\+?\d{7,15}$", regex=True).all(), "Invalid phone numbers found"

print("All validations passed!")

# 4. Load into Postgres
DATABASE_URL = "postgresql+psycopg2://postgres:God4me%402025@localhost:5432/store_db"
engine = create_engine(DATABASE_URL)

df.to_sql("customers", engine, if_exists="replace", index=False)
print("Data successfully loaded into Postgres table 'customers'")
