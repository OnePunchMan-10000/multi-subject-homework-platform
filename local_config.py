# Local development configuration
# Set this to your Railway database public URL to use the same database locally
import os

# Replace this with your actual Railway DATABASE_PUBLIC_URL
RAILWAY_DB_URL = "YOUR_RAILWAY_DATABASE_PUBLIC_URL"

# Set the environment variable so the app connects to Railway PostgreSQL
if RAILWAY_DB_URL != "YOUR_RAILWAY_DATABASE_PUBLIC_URL":
    os.environ["DATABASE_URL"] = RAILWAY_DB_URL
    print(f"✅ Connected to Railway PostgreSQL: {RAILWAY_DB_URL[:20]}...")
else:
    print("⚠️  Please set your Railway DATABASE_PUBLIC_URL in local_config.py")
    print("   This will make local app use the same database as deployed app")
