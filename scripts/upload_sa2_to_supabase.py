import pandas as pd
import sys
import os
from supabase import create_client, Client
from datetime import datetime

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
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

def create_sa2_table_sql():
    """
    Create the SA2 table in Supabase.
    Run this SQL in your Supabase SQL Editor:
    """
    
    sql_create_table = """
    -- Create SA2 table with demographics data
    CREATE TABLE IF NOT EXISTS public.sa2_demographics (
        id BIGSERIAL PRIMARY KEY,
        sa2_code VARCHAR(20) UNIQUE NOT NULL,
        sa2_name VARCHAR(255) NOT NULL,
        total_pop INTEGER,
        pct_youth_18_34 DECIMAL(5,4),
        median_age INTEGER,
        median_weekly_income INTEGER,
        median_weekly_rent INTEGER,
        pct_students DECIMAL(5,4),
        rent_to_income_ratio DECIMAL(5,4),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_sa2_code ON public.sa2_demographics(sa2_code);
    CREATE INDEX IF NOT EXISTS idx_sa2_name ON public.sa2_demographics(sa2_name);
    CREATE INDEX IF NOT EXISTS idx_sa2_population ON public.sa2_demographics(total_pop);
    CREATE INDEX IF NOT EXISTS idx_sa2_income ON public.sa2_demographics(median_weekly_income);

    -- Enable Row Level Security (RLS)
    ALTER TABLE public.sa2_demographics ENABLE ROW LEVEL SECURITY;

    -- Create policy to allow public read access
    CREATE POLICY "Allow public read access" ON public.sa2_demographics
        FOR SELECT USING (true);

    -- Create policy to allow authenticated users to insert/update
    CREATE POLICY "Allow authenticated insert" ON public.sa2_demographics
        FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        
    CREATE POLICY "Allow authenticated update" ON public.sa2_demographics
        FOR UPDATE USING (auth.role() = 'authenticated');
    """
    
    print("=== SA2 TABLE CREATION SQL ===")
    print("Copy and run this SQL in your Supabase SQL Editor:")
    print(sql_create_table)
    print("=" * 50)

def upload_sa2_to_supabase(csv_file_path="data/processed/sa2_full.csv", batch_size=100):
    """
    Upload SA2 demographics data to Supabase in batches.
    
    Args:
        csv_file_path: Path to the SA2 CSV file
        batch_size: Number of records to upload in each batch
    """
    
    print(f"=== UPLOADING SA2 DATA TO SUPABASE ===")
    
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
        required_columns = ['sa2_code', 'sa2_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            return False
        
        # Clean and prepare data
        df = df.dropna(subset=['sa2_code', 'sa2_name'])  # Remove rows with missing required values
        print(f"After cleaning: {len(df)} records")
        
        # Convert to list of dictionaries
        records = []
        for _, row in df.iterrows():
            record = {
                'sa2_code': str(row['sa2_code']).strip(),
                'sa2_name': str(row['sa2_name']).strip(),
                'total_pop': int(row['total_pop']) if pd.notna(row['total_pop']) else None,
                'pct_youth_18_34': float(row['pct_youth_18_34']) if pd.notna(row['pct_youth_18_34']) else None,
                'median_age': int(row['median_age']) if pd.notna(row['median_age']) else None,
                'median_weekly_income': int(row['median_weekly_income']) if pd.notna(row['median_weekly_income']) else None,
                'median_weekly_rent': int(row['median_weekly_rent']) if pd.notna(row['median_weekly_rent']) else None,
                'pct_students': float(row['pct_students']) if pd.notna(row['pct_students']) else None,
                'rent_to_income_ratio': float(row['rent_to_income_ratio']) if pd.notna(row['rent_to_income_ratio']) else None
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
                
                result = supabase.table('sa2_demographics').insert(batch).execute()
                
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

def get_sa2_stats(supabase):
    """Get statistics about uploaded SA2 data."""
    try:
        # Total count
        result = supabase.table('sa2_demographics').select("count", count="exact").execute()
        total_count = result.count
        
        # Sample of data
        result = supabase.table('sa2_demographics').select("*").limit(5).execute()
        sample_data = result.data
        
        print(f"\n=== SA2 DATABASE STATISTICS ===")
        print(f"Total SA2 areas: {total_count}")
        print(f"\nSample data:")
        for record in sample_data:
            print(f"  {record['sa2_code']}: {record['sa2_name']} (Pop: {record['total_pop']})")
            
    except Exception as e:
        print(f"Error getting stats: {e}")

def main():
    """Main function to handle command line arguments and execute upload."""
    
    if len(sys.argv) < 2:
        print("Usage: python upload_sa2_to_supabase.py [--create-table] [--upload] [--stats]")
        print("\nOptions:")
        print("  --create-table  Show SQL to create the SA2 table")
        print("  --upload        Upload SA2 data to Supabase")
        print("  --stats         Show database statistics")
        print("\nExamples:")
        print("  python upload_sa2_to_supabase.py --create-table")
        print("  python upload_sa2_to_supabase.py --upload")
        print("  python upload_sa2_to_supabase.py --upload --stats")
        return
    
    show_create_table = '--create-table' in sys.argv
    do_upload = '--upload' in sys.argv
    show_stats = '--stats' in sys.argv
    
    # Show table creation SQL if requested
    if show_create_table:
        create_sa2_table_sql()
        return
    
    # Upload data if requested
    if do_upload:
        success = upload_sa2_to_supabase()
        if success and show_stats:
            supabase = create_supabase_client()
            if supabase:
                get_sa2_stats(supabase)
    
    # Show stats only if requested
    elif show_stats:
        supabase = create_supabase_client()
        if supabase:
            get_sa2_stats(supabase)

if __name__ == "__main__":
    main() 