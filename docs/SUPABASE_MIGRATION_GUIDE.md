# Supabase Migration Guide

This document describes the changes made to migrate your project from CSV file-based data loading to Supabase database integration.

## Summary of Changes

All CSV-based amenities data loading has been replaced with Supabase database queries while maintaining backwards compatibility with CSV files as fallbacks.

## Files Modified

### 1. New Files Created

#### `src/data/supabase_loader.py`
- **Purpose**: Core Supabase data loading functionality
- **Features**:
  - `SupabaseDataLoader` class for database operations
  - Convenience functions: `load_amenities_data()`, `load_demographics_data()`
  - Filtering by category, suburb, location
  - Statistics and connection testing
  - Automatic column renaming (`latitude`/`longitude` → `lat`/`lon`)

#### `test_supabase_integration.py`
- **Purpose**: Comprehensive test suite for Supabase integration
- **Tests**:
  - Connection and data loading
  - Generic loader compatibility
  - Visualization script compatibility
  - Data quality checks

#### `SUPABASE_MIGRATION_GUIDE.md`
- **Purpose**: Documentation of all migration changes

### 2. Files Updated

#### `src/data/load_data.py`
- **Changes**: 
  - Added Supabase integration alongside existing CSV functionality
  - New functions: `load_amenities()`, `load_demographics()`
  - Automatic fallback from Supabase to CSV if connection fails
  - Smart file detection for multiple CSV versions

#### `visualize_amenities_with_boundaries.py`
- **Changes**:
  - Replaced `pd.read_csv()` calls with `load_amenities_data()`
  - Updated both `create_combined_map()` and `create_amenities_only_map()` functions
  - Added proper error handling for database connections
  - Maintained same output format and functionality

#### `notebooks/python scripts/improved_suburbs_query.py`
- **Changes**:
  - Replaced CSV loading with Supabase data loading
  - Updated `compare_with_original()` function
  - Added database connection error handling

#### `clean_duplicate_amenities.py`
- **Changes**:
  - Added interactive data source selection (Supabase vs CSV)
  - New function: `analyze_duplicates_detailed_supabase()`
  - Updated main execution flow to support both data sources
  - Maintained existing CSV functionality for backwards compatibility

#### `config/supabase_config.py` (New)
- **Purpose**: Configuration file for Supabase credentials
- **Features**:
  - Environment variable support
  - Placeholder values with instructions
  - Security best practices

## Usage Changes

### Before (CSV-based)
```python
# Old way
df_amenities = pd.read_csv('data/processed/melbourne_amenities_improved_20250718_175145_cleaned_20250718_191258.csv')
```

### After (Supabase-based)
```python
# New way
from src.data.supabase_loader import load_amenities_data
df_amenities = load_amenities_data()

# Or with fallback
from src.data.load_data import load_amenities
df_amenities = load_amenities(use_supabase=True)
```

## Key Benefits

1. **Real-time Data**: No need to regenerate CSV files
2. **Centralized Storage**: Single source of truth in the database
3. **Filtering Capabilities**: Query specific suburbs, categories, or locations
4. **Scalability**: Better performance for large datasets
5. **Collaboration**: Multiple users can access the same data
6. **API Access**: Can build web apps and APIs on top of the database

## Backwards Compatibility

All existing functionality is preserved:
- CSV files still work as fallbacks
- Same DataFrame structure and column names
- Existing scripts work without modification (just better data source)
- Error handling maintains graceful degradation

## Database Schema

### `amenities` table structure:
```sql
- id (BIGSERIAL PRIMARY KEY)
- suburb (VARCHAR(255) NOT NULL)
- category (VARCHAR(50) NOT NULL) 
- name (VARCHAR(255) NOT NULL)
- latitude (DOUBLE PRECISION NOT NULL)
- longitude (DOUBLE PRECISION NOT NULL)
- created_at (TIMESTAMP WITH TIME ZONE)
- updated_at (TIMESTAMP WITH TIME ZONE)
```

### Indexes for performance:
- `idx_amenities_suburb` on suburb
- `idx_amenities_category` on category  
- `idx_amenities_location` on (latitude, longitude)

## Migration Steps

1. **Setup Supabase** (if not done):
   ```bash
   python upload_to_supabase.py --create-table
   # Copy SQL to Supabase SQL Editor and run
   ```

2. **Upload Data**:
   ```bash
   python upload_to_supabase.py "your_csv_file.csv" --stats
   ```

3. **Test Integration**:
   ```bash
   python test_supabase_integration.py
   ```

4. **Use Updated Scripts**:
   ```bash
   python visualize_amenities_with_boundaries.py
   python clean_duplicate_amenities.py
   ```

## Available Functions

### Data Loading
```python
from src.data.supabase_loader import *

# Load all amenities
df = load_amenities_data()

# Filter by category
cafes = get_amenities_by_category("cafe")

# Filter by suburb
carlton = get_amenities_by_suburb("Carlton")

# Get unique suburbs list
suburbs = get_unique_suburbs()

# Get statistics
stats = loader.get_amenity_statistics()
```

### Connection Testing
```python
from src.data.supabase_loader import SupabaseDataLoader

loader = SupabaseDataLoader()
if loader.test_connection():
    print("Connected successfully!")
```

## Troubleshooting

### Common Issues

1. **Connection Error**: Check `config/supabase_config.py` credentials
2. **No Data Found**: Ensure data has been uploaded with `upload_to_supabase.py`
3. **Import Errors**: Run `pip install -r requirements.txt`
4. **Permission Denied**: Check RLS policies in Supabase dashboard

### Fallback Behavior

If Supabase connection fails, the system automatically:
1. Logs the error
2. Attempts to load from CSV files
3. Tries multiple CSV file versions
4. Provides helpful error messages

## Performance Notes

- **First Load**: Slightly slower due to network request
- **Subsequent Loads**: Can be cached or filtered for better performance
- **Large Datasets**: Database queries are more efficient than CSV parsing
- **Memory Usage**: Similar to CSV loading

## Security

- Uses Supabase Row Level Security (RLS)
- Environment variable support for credentials
- Public read access, authenticated write access
- Service role key available for admin operations

## Future Enhancements

Potential future improvements:
1. **Caching**: Add local caching for frequently accessed data
2. **Real-time Updates**: Subscribe to database changes
3. **Demographics Migration**: Move demographics data to Supabase
4. **Advanced Filtering**: Geographic queries, full-text search
5. **Data Validation**: Automated data quality checks 