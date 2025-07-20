# Scripts Directory

This directory contains all the main utility scripts for the Melbourne Student Liveability Index project.

## Scripts Overview

### Data Management
- **`upload_to_supabase.py`** - Upload CSV data to Supabase database
- **`clean_duplicate_amenities.py`** - Clean and deduplicate amenities data
- **`query_supabase_example.py`** - Example queries for accessing Supabase data

### Visualization
- **`visualize_amenities_with_boundaries.py`** - Create interactive maps with amenities and demographics

### Testing
- **`test_supabase_integration.py`** - Test suite for Supabase integration

## How to Run Scripts

### From the scripts directory:
```bash
cd scripts
python upload_to_supabase.py ../data/processed/your_file.csv
python visualize_amenities_with_boundaries.py
python test_supabase_integration.py
```

### From the project root:
```bash
cd student-liveability-index-au
python scripts/upload_to_supabase.py data/processed/your_file.csv
python scripts/visualize_amenities_with_boundaries.py
python scripts/test_supabase_integration.py
```

## Configuration

Make sure to configure your Supabase credentials in `../config/supabase_config.py` before running scripts that access the database.

## Output

- Generated maps are saved to `../output/`
- Processed data files are saved to `../data/processed/`

## Dependencies

Install required packages:
```bash
pip install -r ../requirements.txt
``` 