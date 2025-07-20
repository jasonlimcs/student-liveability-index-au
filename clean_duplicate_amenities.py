import pandas as pd
import numpy as np
from datetime import datetime

def clean_duplicate_amenities(input_file, output_file=None):
    """
    Remove duplicate amenities based on name and coordinates.
    
    Parameters:
    input_file: Path to the input CSV file
    output_file: Path for output CSV file (optional, will auto-generate if not provided)
    """
    
    print("=" * 60)
    print("CLEANING DUPLICATE AMENITIES")
    print("=" * 60)
    
    # Load the data
    print(f"Loading data from: {input_file}")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"ERROR: File {input_file} not found!")
        return
    
    print(f"Original dataset: {len(df):,} amenities")
    
    # Show original breakdown
    print(f"\nOriginal breakdown by category:")
    original_counts = df['category'].value_counts()
    for category, count in original_counts.items():
        print(f"  {category}: {count:,}")
    
    print(f"\nOriginal breakdown by suburb (top 10):")
    original_suburbs = df['suburb'].value_counts().head(10)
    for suburb, count in original_suburbs.items():
        print(f"  {suburb}: {count}")
    
    # Round coordinates to avoid floating point precision issues
    # Round to 6 decimal places (~1 meter precision)
    df['lat_rounded'] = df['lat'].round(6)
    df['lon_rounded'] = df['lon'].round(6)
    
    # Create a unique identifier based on name and rounded coordinates
    df['unique_id'] = df['name'].str.lower().str.strip() + '_' + df['lat_rounded'].astype(str) + '_' + df['lon_rounded'].astype(str)
    
    # Find duplicates
    print(f"\n" + "-" * 40)
    print("IDENTIFYING DUPLICATES")
    print("-" * 40)
    
    duplicate_mask = df.duplicated(subset=['unique_id'], keep=False)
    duplicates = df[duplicate_mask].copy()
    
    if len(duplicates) > 0:
        print(f"Found {len(duplicates):,} duplicate records")
        
        # Show examples of duplicates
        print(f"\nExample duplicates:")
        unique_duplicate_groups = duplicates.groupby('unique_id')
        
        example_count = 0
        for unique_id, group in unique_duplicate_groups:
            if example_count >= 5:  # Show only first 5 examples
                break
            
            name = group.iloc[0]['name']
            lat = group.iloc[0]['lat']
            lon = group.iloc[0]['lon']
            suburbs = ', '.join(group['suburb'].unique())
            categories = ', '.join(group['category'].unique())
            
            print(f"  {name} ({lat:.4f}, {lon:.4f})")
            print(f"    Found in suburbs: {suburbs}")
            print(f"    Categories: {categories}")
            print(f"    Total duplicates: {len(group)}")
            print()
            
            example_count += 1
        
        if len(unique_duplicate_groups) > 5:
            print(f"  ... and {len(unique_duplicate_groups) - 5} more duplicate groups")
    
    # Strategy for handling duplicates
    print(f"\n" + "-" * 40)
    print("DEDUPLICATION STRATEGY")
    print("-" * 40)
    
    def choose_best_duplicate(group):
        """
        Choose the best record from a group of duplicates.
        Priority:
        1. Prefer records with more specific/recognizable suburb names
        2. Prefer records with non-"Unnamed" names
        3. If tied, keep the first one
        """
        
        # If all records are identical, just keep the first
        if len(group['suburb'].unique()) == 1:
            return group.iloc[0]
        
        # Prefer certain suburbs (more central/well-known areas)
        preferred_suburbs = [
            'Melbourne', 'Carlton', 'Fitzroy', 'Richmond', 'South Yarra', 
            'Prahran', 'St Kilda', 'South Melbourne', 'Southbank', 'Docklands'
        ]
        
        for preferred in preferred_suburbs:
            matches = group[group['suburb'] == preferred]
            if len(matches) > 0:
                return matches.iloc[0]
        
        # Prefer non-"Unnamed" entries
        named_entries = group[~group['name'].str.contains('Unnamed', case=False, na=False)]
        if len(named_entries) > 0:
            return named_entries.iloc[0]
        
        # Default: return first record
        return group.iloc[0]
    
    # Remove duplicates by keeping the "best" record from each group
    print("Applying deduplication...")
    
    # Group by unique_id and apply the selection function
    unique_amenities = []
    duplicate_groups = df.groupby('unique_id')
    
    for unique_id, group in duplicate_groups:
        if len(group) > 1:
            # Multiple records - choose the best one
            best_record = choose_best_duplicate(group)
            unique_amenities.append(best_record)
        else:
            # Single record - keep as is
            unique_amenities.append(group.iloc[0])
    
    # Create cleaned dataframe
    df_clean = pd.DataFrame(unique_amenities)
    
    # Remove the helper columns
    df_clean = df_clean.drop(['lat_rounded', 'lon_rounded', 'unique_id'], axis=1)
    
    # Reset index
    df_clean = df_clean.reset_index(drop=True)
    
    # Show results
    print(f"\n" + "=" * 60)
    print("CLEANING RESULTS")
    print("=" * 60)
    
    print(f"Original amenities: {len(df):,}")
    print(f"Cleaned amenities: {len(df_clean):,}")
    print(f"Removed duplicates: {len(df) - len(df_clean):,}")
    print(f"Reduction: {((len(df) - len(df_clean)) / len(df) * 100):.1f}%")
    
    # Show cleaned breakdown
    print(f"\nCleaned breakdown by category:")
    cleaned_counts = df_clean['category'].value_counts()
    for category, count in cleaned_counts.items():
        original_count = original_counts.get(category, 0)
        reduction = original_count - count
        print(f"  {category}: {count:,} (was {original_count:,}, removed {reduction:,})")
    
    print(f"\nCleaned breakdown by suburb (top 10):")
    cleaned_suburbs = df_clean['suburb'].value_counts().head(10)
    for suburb, count in cleaned_suburbs.items():
        print(f"  {suburb}: {count}")
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_base = input_file.replace('.csv', '')
        output_file = f"{input_base}_cleaned_{timestamp}.csv"
    
    # Save cleaned data
    df_clean.to_csv(output_file, index=False)
    print(f"\nCleaned data saved to: {output_file}")
    
    return df_clean, output_file

def analyze_duplicates_detailed(input_file):
    """Provide detailed analysis of duplicates before cleaning."""
    
    print("=" * 60)
    print("DETAILED DUPLICATE ANALYSIS")
    print("=" * 60)
    
    df = pd.read_csv(input_file)
    
    # Round coordinates
    df['lat_rounded'] = df['lat'].round(6)
    df['lon_rounded'] = df['lon'].round(6)
    df['unique_id'] = df['name'].str.lower().str.strip() + '_' + df['lat_rounded'].astype(str) + '_' + df['lon_rounded'].astype(str)
    
    # Find all duplicate groups
    duplicate_groups = df[df.duplicated(subset=['unique_id'], keep=False)].groupby('unique_id')
    
    print(f"Total duplicate groups: {len(duplicate_groups)}")
    print(f"Total duplicate records: {sum(len(group) for _, group in duplicate_groups)}")
    
    # Analyze by category
    print(f"\nDuplicate patterns by category:")
    for category in df['category'].unique():
        cat_data = df[df['category'] == category]
        cat_duplicates = cat_data[cat_data.duplicated(subset=['unique_id'], keep=False)]
        print(f"  {category}: {len(cat_duplicates)} duplicate records in {len(cat_duplicates.groupby('unique_id'))} groups")
    
    # Show worst offenders
    print(f"\nTop 10 most duplicated amenities:")
    duplicate_counts = {}
    for unique_id, group in duplicate_groups:
        name = group.iloc[0]['name']
        duplicate_counts[name] = len(group)
    
    sorted_duplicates = sorted(duplicate_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (name, count) in enumerate(sorted_duplicates[:10], 1):
        print(f"  {i:2d}. {name}: {count} duplicates")
    
    # Analyze cross-suburb duplicates
    print(f"\nCross-suburb duplicate analysis:")
    cross_suburb_count = 0
    for unique_id, group in duplicate_groups:
        if len(group['suburb'].unique()) > 1:
            cross_suburb_count += 1
    
    print(f"  Amenities appearing in multiple suburbs: {cross_suburb_count}")
    print(f"  Amenities with exact duplicates in same suburb: {len(duplicate_groups) - cross_suburb_count}")

if __name__ == "__main__":
    # Configuration
    input_file = "data/processed/melbourne_amenities_improved_20250718_175145.csv"
    
    print("Choose an option:")
    print("1. Analyze duplicates (no changes)")
    print("2. Clean duplicates")
    print("3. Both")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        analyze_duplicates_detailed(input_file)
        print("\n" + "=" * 60 + "\n")
    
    if choice in ['2', '3']:
        cleaned_df, output_file = clean_duplicate_amenities(input_file)
        
        print(f"\nSUCCESS!")
        print(f"Cleaned amenities dataset saved as: {output_file}")
        print(f"You can now update your visualization script to use this cleaned file.")
        
        # Suggest next step
        print(f"\nNext step: Update your visualization script:")
        print(f"  Change: df_amenities = pd.read_csv('{input_file}')")
        print(f"  To:     df_amenities = pd.read_csv('{output_file}')") 