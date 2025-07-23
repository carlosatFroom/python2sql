#!/usr/bin/env python3
"""
Load Excel spreadsheet data into MySQL database using df.to_sql()
Creates tables named {spreadsheet_name}_{sheet_name}
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# ----------------------------------------------------------- #
# 1. Load environment variables
# ----------------------------------------------------------- #
load_dotenv()

# ----------------------------------------------------------- #
# 2. Configuration
# ----------------------------------------------------------- #
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_USER = os.getenv("DB_USER") 
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "buckets"

# Excel file to process
EXCEL_FILE = "buckets.xlsx"

# ----------------------------------------------------------- #
# 3. Create SQLAlchemy engine and ensure database exists
# ----------------------------------------------------------- #
# First connect without database to create it if needed
engine_no_db = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}")
with engine_no_db.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4"))

# Now connect to the specific database
engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ----------------------------------------------------------- #
# 4. Process Excel file - read all sheets
# ----------------------------------------------------------- #
try:
    # Get spreadsheet name without extension
    spreadsheet_name = Path(EXCEL_FILE).stem
    
    # Read all sheets from Excel file
    all_sheets = pd.read_excel(EXCEL_FILE, sheet_name=None)
    
    print(f"Found {len(all_sheets)} sheet(s) in {EXCEL_FILE}")
    
    for sheet_name, df in all_sheets.items():
        # Normalize column names
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        
        # Create table name as {spreadsheet_name}_{sheet_name}
        table_name = f"{spreadsheet_name}_{sheet_name}".lower().replace(' ', '_')
        
        # Use df.to_sql() to create table and insert data
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='replace',  # Replace table if it exists
            index=False,          # Don't include DataFrame index
            method='multi'        # Use executemany for better performance
        )
        
        print(f"✅ Created table '{table_name}' with {len(df)} rows")
    
    print(f"\n🎉 Successfully processed all sheets from {EXCEL_FILE}")
    
except FileNotFoundError:
    print(f"❌ Error: Excel file '{EXCEL_FILE}' not found")
    raise SystemExit(1)
except Exception as e:
    print(f"❌ Error processing Excel file: {e}")
    raise SystemExit(1)
