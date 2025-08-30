#!/usr/bin/env python
"""
Test script for Supabase connection using the official method.
Based on Supabase Python connection instructions.
"""
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

print("🔍 Testing Supabase connection...")
print(f"Host: {HOST}")
print(f"Port: {PORT}")
print(f"User: {USER}")
print(f"Database: {DBNAME}")

# Try both methods - individual params and connection string
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"🔗 Method 1 - Individual parameters:")
print(f"   user='{USER}'")
print(f"   host='{HOST}'")
print(f"   port='{PORT}'")
print(f"   dbname='{DBNAME}'")

print(f"\n🔗 Method 2 - Connection string:")
print(f"   DATABASE_URL='{DATABASE_URL}'")

# Try connection string first
try:
    print(f"\n🔄 Trying connection string method...")
    connection = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful with DATABASE_URL!")

except Exception as e:
    print(f"❌ DATABASE_URL failed: {e}")

    # Try individual parameters
    try:
        print(f"\n🔄 Trying individual parameters method...")
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("✅ Connection successful with individual parameters!")

    except Exception as e2:
        print(f"❌ Individual parameters failed: {e2}")
        raise e2
    print("✅ Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("🕐 Current Time:", result)
    
    # Test Django tables
    try:
        cursor.execute("SELECT COUNT(*) FROM django_migrations;")
        migrations_count = cursor.fetchone()[0]
        print(f"📊 Django migrations: {migrations_count}")
    except Exception as e:
        print(f"⚠️  Django tables not found: {e}")

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("🔒 Connection closed.")

except Exception as e:
    print(f"❌ Failed to connect: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Check your .env file exists")
    print("2. Verify Supabase credentials")
    print("3. Ensure network connectivity")
