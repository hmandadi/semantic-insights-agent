# test_db.py

from src.db import execute_query

df = execute_query("""
SELECT
    region_name
FROM dim_region
""")

print(df)