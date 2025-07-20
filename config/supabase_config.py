"""
Supabase Configuration

To use this:
1. Go to your Supabase project dashboard
2. Get your project URL and anon key from Settings > API
3. Update the values below
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase credentials - update these with your actual values
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your_supabase_project_url_here')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your_supabase_anon_key_here')

# Alternatively, you can set them directly here (less secure):
# SUPABASE_URL = "https://your-project.supabase.co"
# SUPABASE_KEY = "your_anon_key_here" 