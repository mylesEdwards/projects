import psycopg2
from pymongo import MongoClient
import certifi

print("=== POSTGRESQL DIAGNOSTIC ===")
try:
    conn = psycopg2.connect(dbname="ecommerce_hybrid", user="myles", host="localhost")
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM orders;")
    print(f"Total Orders saved: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM order_items;")
    print(f"Total Order Items saved: {cur.fetchone()[0]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Postgres Error: {e}")

print("\n=== MONGODB DIAGNOSTIC ===")
try:
    uri = "mongodb+srv://myleszero5_db_user:ACS_Project2026@cluster0.3xd4wo3.mongodb.net/"
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client['ecommerce_hybrid']
    
    # Grab exactly ONE document to see what it looks like
    sample_doc = db.user_activity.find_one()
    
    if sample_doc:
        print("Successfully found data! Here is what one document looks like:")
        for key, value in sample_doc.items():
            print(f"  {key}: {value} (Type: {type(value).__name__})")
    else:
        print("The user_activity collection is completely empty!")
        
except Exception as e:
    print(f"MongoDB Error: {e}")