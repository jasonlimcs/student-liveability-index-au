import pandas as pd
import sys
import os
from supabase import create_client, Client
from datetime import datetime

# Add config directory to path
sys.path.append('../config')
from supabase_config import SUPABASE_URL, SUPABASE_KEY

def create_supabase_client():
    """Initialize Supabase client."""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        print("Please check your SUPABASE_URL and SUPABASE_KEY in config/supabase_config.py")
        return None

def create_amenities_table(supabase):
    """
    Create the amenities table in Supabase.
    Run this SQL in your Supabase SQL Editor:
    """
    
    sql_create_table = """
    -- Create amenities table
    CREATE TABLE IF NOT EXISTS public.amenities (
        id BIGSERIAL PRIMARY KEY,
        suburb VARCHAR(255) NOT NULL,
        category VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_amenities_suburb ON public.amenities(suburb);
    CREATE INDEX IF NOT EXISTS idx_amenities_category ON public.amenities(category);
    CREATE INDEX IF NOT EXISTS idx_amenities_location ON public.amenities(latitude, longitude);

    -- Enable Row Level Security (RLS)
    ALTER TABLE public.amenities ENABLE ROW LEVEL SECURITY;

    -- Create policy to allow public read access
    CREATE POLICY "Allow public read access" ON public.amenities
        FOR SELECT USING (true);

    -- Create policy to allow authenticated users to insert
    CREATE POLICY "Allow authenticated insert" ON public.amenities
        FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    """
    
    print("=== TABLE CREATION SQL ===")
    print("Copy and run this SQL in your Supabase SQL Editor:")
    print(sql_create_table)
    print("=" * 50)

def upload_csv_to_supabase(csv_file_path, table_name="amenities", batch_size=100):
    """
    Upload CSV data to Supabase in batches.
    
    Args:
        csv_file_path: Path to the CSV file
        table_name: Name of the Supabase table
        batch_size: Number of records to upload in each batch
    """
    
    print(f"=== UPLOADING {csv_file_path} TO SUPABASE ===")
    
    # Initialize Supabase client
    supabase = create_supabase_client()
    if not supabase:
        return False
    
    try:
        # Read CSV file
        print(f"Reading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        print(f"Found {len(df)} records")
        
        # Validate required columns
        required_columns = ['suburb', 'category', 'name', 'lat', 'lon']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            return False
        
        # Clean and prepare data
        df = df.dropna()  # Remove rows with missing values
        print(f"After cleaning: {len(df)} records")
        
        # Convert to list of dictionaries and rename lat/lon columns
        records = []
        for _, row in df.iterrows():
            record = {
                'suburb': str(row['suburb']),
                'category': str(row['category']),
                'name': str(row['name']),
                'latitude': float(row['lat']),
                'longitude': float(row['lon'])
            }
            records.append(record)
        
        # Upload in batches
        total_uploaded = 0
        total_batches = (len(records) + batch_size - 1) // batch_size
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            try:
                print(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} records)...")
                
                result = supabase.table(table_name).insert(batch).execute()
                
                if result.data:
                    total_uploaded += len(batch)
                    print(f"  SUCCESS: Successfully uploaded {len(batch)} records")
                else:
                    print(f"  FAILED: Failed to upload batch {batch_num}")
                    
            except Exception as e:
                print(f"  ERROR: Error uploading batch {batch_num}: {e}")
                continue
        
        print(f"\n=== UPLOAD COMPLETE ===")
        print(f"Total records uploaded: {total_uploaded}/{len(records)}")
        print(f"Success rate: {(total_uploaded/len(records)*100):.1f}%")
        
        return total_uploaded > 0
        
    except Exception as e:
        print(f"Error reading CSV or uploading data: {e}")
        return False

def get_upload_stats(supabase, table_name="amenities"):
    """Get statistics about uploaded data."""
    try:
        # Total count
        result = supabase.table(table_name).select("count", count="exact").execute()
        total_count = result.count
        
        # Count by category
        result = supabase.table(table_name).select("category").execute()
        df = pd.DataFrame(result.data)
        category_counts = df['category'].value_counts()
        
        # Count by suburb (top 10)
        result = supabase.table(table_name).select("suburb").execute()
        df = pd.DataFrame(result.data)
        suburb_counts = df['suburb'].value_counts().head(10)
        
        print(f"\n=== DATABASE STATISTICS ===")
        print(f"Total amenities: {total_count}")
        print(f"\nBy category:")
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
        print(f"\nTop 10 suburbs:")
        for suburb, count in suburb_counts.items():
            print(f"  {suburb}: {count}")
            
    except Exception as e:
        print(f"Error getting stats: {e}")

def main():
    """Main function to handle command line arguments and execute upload."""
    
    if len(sys.argv) < 2:
        print("Usage: python upload_to_supabase.py <csv_file_path> [--create-table] [--stats]")
        print("\nOptions:")
        print("  --create-table  Show SQL to create the table")
        print("  --stats         Show database statistics after upload")
        print("\nExample:")
        print("  python upload_to_supabase.py ../data/processed/melbourne_amenities_improved_20250718_175145_cleaned_20250718_191258.csv")
        print("\nTo create table:")
        print("  python upload_to_supabase.py --create-table")
        return
    
    show_create_table = '--create-table' in sys.argv
    show_stats = '--stats' in sys.argv
    
    # Show table creation SQL if requested (no file needed)
    if show_create_table:
        create_amenities_table(None)
        return
    
    # For upload operations, we need a CSV file
    csv_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found")
        return
    
    # Upload data
    success = upload_csv_to_supabase(csv_file)
    
    if success and show_stats:
        supabase = create_supabase_client()
        if supabase:
            get_upload_stats(supabase)

if __name__ == "__main__":
    main() 