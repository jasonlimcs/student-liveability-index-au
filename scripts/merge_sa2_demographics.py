import pandas as pd

# Load SA2 names
sa2_names = pd.read_csv('data/raw/sa2_names.csv', usecols=[0, 1], names=['sa2_code', 'sa2_name'], header=0, dtype={'sa2_code': str})
sa2_names = sa2_names[['sa2_code', 'sa2_name']]
sa2_names['sa2_code'] = sa2_names['sa2_code'].astype(str).str.strip()

# Load demographics
demographics = pd.read_csv('data/processed/abs_demographics_merged.csv', dtype={'sa2_code': str})
demographics['sa2_code'] = demographics['sa2_code'].astype(str).str.strip()

# Merge on sa2_code
merged = pd.merge(sa2_names, demographics, on='sa2_code', how='left')

# Save to processed
merged.to_csv('data/processed/sa2_full.csv', index=False)

print(f"Merged table saved to data/processed/sa2_full.csv with {len(merged)} rows.") 