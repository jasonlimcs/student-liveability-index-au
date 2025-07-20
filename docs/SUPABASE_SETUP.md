# Supabase Setup Guide

This guide will help you upload your Melbourne amenities data to a Supabase database.

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Choose your organization
5. Fill in project details:
   - Name: "Melbourne Amenities" (or any name you prefer)
   - Database Password: Choose a strong password
   - Region: Choose closest to Australia
6. Click "Create new project"

## Step 2: Get Your Project Credentials

1. In your Supabase dashboard, go to **Settings > API**
2. Copy these values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public key** (starts with `eyJhbGciOi...`)

## Step 3: Configure Your Local Environment

### Option A: Using .env file (Recommended)
1. Create a `.env` file in your project root:
```bash
SUPABASE_URL=your_project_url_here
SUPABASE_KEY=your_anon_key_here
```

### Option B: Direct configuration
1. Edit `config/supabase_config.py`
2. Replace the placeholder values:
```python
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your_anon_key_here"
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Create the Database Table

1. First, generate the SQL:
```bash
python upload_to_supabase.py dummy --create-table
```

2. Copy the SQL output
3. Go to your Supabase dashboard > **SQL Editor**
4. Paste and run the SQL to create the table

## Step 6: Upload Your Data

Upload your cleaned amenities data:
```bash
python upload_to_supabase.py "data/processed/melbourne_amenities_improved_20250718_175145_cleaned_20250718_191258.csv" --stats
```

## Step 7: Verify Your Data

After upload, you can:

1. **Check in Supabase dashboard**: Go to **Table Editor > amenities**
2. **Query your data** using the built-in SQL editor
3. **Use the API** to fetch data programmatically

### Example queries:

```sql
-- Count amenities by category
SELECT category, COUNT(*) as count 
FROM amenities 
GROUP BY category 
ORDER BY count DESC;

-- Find all cafes in Carlton
SELECT name, latitude, longitude 
FROM amenities 
WHERE suburb = 'Carlton' AND category = 'cafe';

-- Find amenities near a specific location (within ~1km)
SELECT name, suburb, category,
       ABS(latitude - (-37.8136)) + ABS(longitude - 144.9631) as distance
FROM amenities 
WHERE ABS(latitude - (-37.8136)) + ABS(longitude - 144.9631) < 0.01
ORDER BY distance;
```

## Troubleshooting

### Common Issues:

1. **Authentication Error**: Check your SUPABASE_URL and SUPABASE_KEY
2. **Table doesn't exist**: Make sure you ran the CREATE TABLE SQL first
3. **Permission denied**: Check your RLS policies in Supabase dashboard

### Getting Help:

- Check the Supabase [documentation](https://supabase.com/docs)
- View your project logs in the Supabase dashboard
- Test your connection with a simple query first

## Next Steps

Once your data is uploaded, you can:
- Build a web app to visualize the data
- Create an API to serve the data
- Set up real-time subscriptions for data changes
- Add more sophisticated queries and analytics 