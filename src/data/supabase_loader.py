import pandas as pd
import sys
import os
from typing import Optional, List, Dict, Any

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from supabase_config import SUPABASE_URL, SUPABASE_KEY

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase package not found. Install with: pip install supabase")
    sys.exit(1)

class SupabaseDataLoader:
    """Data loader for accessing amenities and demographics data from Supabase."""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Initialize Supabase client connection."""
        try:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("SUCCESS: Connected to Supabase database")
        except Exception as e:
            print(f"ERROR: Error connecting to Supabase: {e}")
            print("Check your SUPABASE_URL and SUPABASE_KEY in config/supabase_config.py")
            self.supabase = None
    
    def get_all_amenities(self) -> pd.DataFrame:
        """Get all amenities data from Supabase."""
        if not self.supabase:
            print("No Supabase connection available")
            return pd.DataFrame()
        
        try:
            result = self.supabase.table("amenities").select("*").execute()
            df = pd.DataFrame(result.data)
            
            if not df.empty:
                # Rename columns to match CSV format (lat, lon instead of latitude, longitude)
                df = df.rename(columns={
                    'latitude': 'lat', 
                    'longitude': 'lon'
                })
                print(f"SUCCESS: Loaded {len(df)} amenity records from database")
            else:
                print("WARNING: No amenities found in database")
            
            return df
            
        except Exception as e:
            print(f"ERROR: Error loading amenities: {e}")
            return pd.DataFrame()
    
    def get_amenities_by_category(self, category: str) -> pd.DataFrame:
        """Get amenities filtered by category."""
        if not self.supabase:
            return pd.DataFrame()
        
        try:
            result = self.supabase.table("amenities").select("*").eq("category", category).execute()
            df = pd.DataFrame(result.data)
            
            if not df.empty:
                df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
                print(f"SUCCESS: Loaded {len(df)} {category} records")
            
            return df
            
        except Exception as e:
            print(f"ERROR: Error loading {category}s: {e}")
            return pd.DataFrame()
    
    def get_amenities_by_suburb(self, suburb: str) -> pd.DataFrame:
        """Get amenities filtered by suburb."""
        if not self.supabase:
            return pd.DataFrame()
        
        try:
            result = self.supabase.table("amenities").select("*").eq("suburb", suburb).execute()
            df = pd.DataFrame(result.data)
            
            if not df.empty:
                df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
                print(f"SUCCESS: Loaded {len(df)} amenities in {suburb}")
            
            return df
            
        except Exception as e:
            print(f"ERROR: Error loading amenities for {suburb}: {e}")
            return pd.DataFrame()
    
    def get_unique_suburbs(self) -> List[str]:
        """Get list of unique suburbs from the database."""
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.table("amenities").select("suburb").execute()
            df = pd.DataFrame(result.data)
            
            if not df.empty:
                suburbs = df['suburb'].unique().tolist()
                print(f"SUCCESS: Found {len(suburbs)} unique suburbs")
                return sorted(suburbs)
            
            return []
            
        except Exception as e:
            print(f"ERROR: Error getting suburbs: {e}")
            return []
    
    def get_amenity_statistics(self) -> Dict[str, Any]:
        """Get statistics about amenities data."""
        df = self.get_all_amenities()
        
        if df.empty:
            return {}
        
        stats = {
            'total_amenities': len(df),
            'categories': df['category'].value_counts().to_dict(),
            'suburbs': df['suburb'].value_counts().to_dict(),
            'unique_categories': df['category'].nunique(),
            'unique_suburbs': df['suburb'].nunique()
        }
        
        return stats
    
    def test_connection(self) -> bool:
        """Test if connection to Supabase is working."""
        if not self.supabase:
            return False
        
        try:
            result = self.supabase.table("amenities").select("count", count="exact").limit(1).execute()
            print(f"SUCCESS: Connection test successful. Database contains {result.count} amenities.")
            return True
        except Exception as e:
            print(f"ERROR: Connection test failed: {e}")
            return False

    def get_all_safety_scores(self) -> pd.DataFrame:
        """Get all safety scores data from Supabase."""
        if not self.supabase:
            print("No Supabase connection available")
            return pd.DataFrame()
        try:
            result = self.supabase.table("safety_scores").select("*").execute()
            df = pd.DataFrame(result.data)
            if not df.empty:
                print(f"SUCCESS: Loaded {len(df)} safety score records from database")
            else:
                print("WARNING: No safety scores found in database")
            return df
        except Exception as e:
            print(f"ERROR: Error loading safety scores: {e}")
            return pd.DataFrame()

# Global instance for easy importing
loader = SupabaseDataLoader()

# Convenience functions for backwards compatibility
def load_amenities_data() -> pd.DataFrame:
    """Load all amenities data from Supabase (replaces CSV loading)."""
    return loader.get_all_amenities()

def load_demographics_data() -> pd.DataFrame:
    """Load demographics data from CSV (fallback until demographics are in Supabase)."""
    import os
    try:
        # Use robust path relative to project root or this file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(base_dir, 'data', 'processed', 'abs_demographics_merged.csv')
        df = pd.read_csv(csv_path)
        print(f"SUCCESS: Loaded {len(df)} demographic records from CSV")
        return df
    except FileNotFoundError:
        print(f"WARNING: Demographics CSV file not found at {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERROR: Error loading demographics: {e}")
        return pd.DataFrame()

def load_safety_scores() -> pd.DataFrame:
    """Load all safety scores from Supabase."""
    return loader.get_all_safety_scores()

def get_amenities_by_category(category: str) -> pd.DataFrame:
    """Get amenities by category from Supabase."""
    return loader.get_amenities_by_category(category)

def get_amenities_by_suburb(suburb: str) -> pd.DataFrame:
    """Get amenities by suburb from Supabase."""
    return loader.get_amenities_by_suburb(suburb)

def get_unique_suburbs() -> List[str]:
    """Get unique suburbs list from Supabase."""
    return loader.get_unique_suburbs()

if __name__ == "__main__":
    # Test the connection and show some stats
    print("=== SUPABASE DATA LOADER TEST ===")
    
    if loader.test_connection():
        stats = loader.get_amenity_statistics()
        if stats:
            print(f"\nDatabase Statistics:")
            print(f"Total amenities: {stats['total_amenities']}")
            print(f"Categories: {stats['unique_categories']}")
            print(f"Suburbs: {stats['unique_suburbs']}")
            
            print(f"\nTop categories:")
            for cat, count in list(stats['categories'].items())[:5]:
                print(f"  {cat}: {count}") 