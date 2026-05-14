import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# Add a title to your web app
st.title("Retail Orders Data Processing Dashboard")

# =========================
# 1. LOAD DATA
# =========================
st.header("1. Load Data")
# Note: Ensure "orders.csv" is in the same directory, or provide the full path
df = pd.read_csv("orders.csv")

st.write("**Initial Shape:**", df.shape)
st.write("**Initial Dtypes:**")
st.write(df.dtypes)

# =========================
# 2. DATA CLEANING
# =========================
st.header("2. Data Cleaning & Type Fixing")

# Standardize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Fix wrong column name
if "postel_code" in df.columns:
    df.rename(columns={"postel_code": "postal_code"}, inplace=True)

# Trim spaces in text columns
text_cols = df.select_dtypes(include=["object", "string"]).columns
for col in text_cols:
    df[col] = df[col].astype("string").str.strip()

# Handle missing values properly
numeric_cols = df.select_dtypes(include="number").columns
df[numeric_cols] = df[numeric_cols].fillna(0)
df[text_cols] = df[text_cols].fillna("Unknown")

# =========================
# 3. FIX DATA TYPES
# =========================
# Convert order_date to datetime
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# Ensure correct types
df["discount_percent"] = df["discount_percent"].astype(float)
df["product_id"] = df["product_id"].astype("string")
df["postal_code"] = df["postal_code"].astype("string")

st.success("Data successfully cleaned and types fixed!")

# =========================
# 4. FEATURE ENGINEERING
# =========================
st.header("3. Feature Engineering")

# Calculate metrics
df["discount_amount"] = (df["list_price"] * df["discount_percent"]) / 100
df["sale_price"] = df["list_price"] - df["discount_amount"]
df["revenue"] = df["sale_price"] * df["quantity"]
df["profit_per_unit"] = df["sale_price"] - df["cost_price"]
df["profit"] = df["profit_per_unit"] * df["quantity"]

# Extract year and month
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month

st.write("**Cleaned Data Info (Shape):**", df.shape)

st.write("**Sample Data:**")
# st.dataframe makes the table interactive (scrollable, sortable) in the browser
st.dataframe(df.head())

# =========================
# 5. SAVE CLEAN DATA & SQL
# =========================
st.header("4. Export to CSV & SQL")

# Save to CSV
df.to_csv("cleaned_orders.csv", index=False)
st.write("✅ Cleaned dataset saved as `cleaned_orders.csv`")

# Save to SQLite
engine = create_engine("sqlite:///retail_orders.db")
df.to_sql("orders", con=engine, if_exists="replace", index=False)
st.write("✅ Data successfully loaded into SQL database: `retail_orders.db`")

# Final success message
st.balloons() # Just a fun Streamlit effect to show it finished!
