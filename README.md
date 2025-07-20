# Melbourne Student Liveability Index

A comprehensive analysis of student liveability in Melbourne using amenities data and demographic information.

## Project Structure

```
student-liveability-index-au/
├── scripts/              # Main utility scripts
│   ├── upload_to_supabase.py
│   ├── visualize_amenities_with_boundaries.py
│   ├── clean_duplicate_amenities.py
│   ├── test_supabase_integration.py
│   └── query_supabase_example.py
├── src/                  # Source code modules
│   └── data/            # Data loading utilities
├── config/              # Configuration files
├── data/                # Data files
│   ├── processed/       # Cleaned data
│   ├── raw/            # Original data
│   ├── interim/        # Intermediate processing
│   └── external/       # External datasets
├── notebooks/           # Jupyter notebooks for analysis
├── docs/               # Documentation
├── output/             # Generated files (maps, reports)
└── map_versions/       # Historical map versions
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Supabase (optional):**
   - See `docs/SUPABASE_SETUP.md` for database setup
   - Configure credentials in `config/supabase_config.py`

3. **Run scripts:**
   ```bash
   cd scripts
   python visualize_amenities_with_boundaries.py
   python test_supabase_integration.py
   ```

## Features

- **Data Integration:** Supabase database with CSV fallbacks
- **Interactive Maps:** Folium-based visualizations with demographic overlays
- **Data Cleaning:** Automated duplicate removal and validation
- **Scalable Architecture:** Modular design with proper separation of concerns

## Documentation

- **Setup:** `docs/SUPABASE_SETUP.md`
- **Migration Guide:** `docs/SUPABASE_MIGRATION_GUIDE.md`
- **Scripts:** `scripts/README.md`