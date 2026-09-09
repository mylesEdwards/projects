import psycopg2
from pymongo import MongoClient
import sys

import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

def test_connections():
    print("--- Starting Connection Test ---")
    
    # 1. Test PostgreSQL (Local)
    try:
        pg_conn = psycopg2.connect(
            dbname="ecommerce_hybrid",
            user="myles", 
            password="", # Usually blank for Homebrew installs
            host="localhost"
        )
        print("✅ PostgreSQL: Connected!")
        pg_conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL Failed: {e}")

    # 2. Test MongoDB (Cloud)
    try:
        # REPLACE 'your_password' with your actual Atlas password!
        uri = "mongodb+srv://myleszero5_db_user:ACS_Project2026@cluster0.3xd4wo3.mongodb.net/"
        client = MongoClient(uri)
        client.admin.command('ping')
        print("✅ MongoDB Atlas: Connected!")
        client.close()
    except Exception as e:
        print(f"❌ MongoDB Failed: {e}")
import pandas as pd

def load_products_to_mongo():
    print("--- Loading Products to MongoDB ---")
    # Load the products CSV
    df = pd.read_csv('olist_products_dataset.csv')
    
    # Connect to Mongo
    uri = "mongodb+srv://myleszero5_db_user:ACS_Project2026@cluster0.3xd4wo3.mongodb.net/"
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client['ecommerce_db']
    collection = db['products']
    
    # Convert dataframe to a list of dictionaries for Mongo
    data_dict = df.to_dict("records")
    
    # Insert into Mongo
    collection.insert_many(data_dict)
    print(f"✅ Successfully loaded {len(data_dict)} products into MongoDB Atlas!")
    client.close()

def load_users_to_postgres():
    print("--- Loading Users to PostgreSQL ---")
    try:
        # 1. Load the customer data from your CSV
        df = pd.read_csv('olist_customers_dataset.csv')
        
        # 2. Prepare the data (Mapping Olist IDs to your schema)
        # We'll use the unique customer_id as a dummy email for now
        users_to_load = df[['customer_id']].head(2000).copy() 
        users_to_load['email'] = users_to_load['customer_id'] + "@olist.com"
        users_to_load['password_hash'] = "default_secure_hash"

        # 3. Connect and Insert
        conn = psycopg2.connect(dbname="ecommerce_hybrid", user="myles", host="localhost")
        cur = conn.cursor()
        
        for _, row in users_to_load.iterrows():
            cur.execute(
                "INSERT INTO Users (email, password_hash) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (row['email'], row['password_hash'])
            )
        
        conn.commit()
        print(f"✅ Successfully loaded {len(users_to_load)} users into PostgreSQL!")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ PostgreSQL Load Failed: {e}")

def load_orders_and_items():
    print("--- Loading Orders to PostgreSQL ---")
    
    # 1. Load the data
    orders_df = pd.read_csv('olist_orders_dataset.csv')
    items_df = pd.read_csv('olist_order_items_dataset.csv')
    
    # 2. Connect
    conn = psycopg2.connect(dbname="ecommerce_hybrid", user="myles", host="localhost")
    cur = conn.cursor()

    try:
        cur.execute("SELECT email FROM users")
        emails = [row[0] for row in cur.fetchall()]
        
        valid_orders = orders_df[orders_df['customer_id'].isin([e.split('@')[0] for e in emails])].head(500)
        successful_orders = 0
        
        for _, row in valid_orders.iterrows():
            try:
                # Get User ID
                cur.execute("SELECT user_id FROM users WHERE email = %s", (row['customer_id'] + "@olist.com",))
                postgres_user_id = cur.fetchone()[0]
                
                # Insert Order
                cur.execute(
                    "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, %s) RETURNING order_id",
                    (postgres_user_id, 0.0, row['order_status']) 
                )
                
                result = cur.fetchone()
                if result:
                     new_order_id = result[0]
                else:
                    print(f"Warning: No order_id returned for {row['customer_id']}!")
                    continue
                
                # Insert Items
                specific_items = items_df[items_df['order_id'] == row['order_id']]
                for _, item in specific_items.iterrows():
                    # THE FIX: Exactly 4 columns, 4 %s placeholders, and 4 variables!
                    cur.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, %s, %s)",
                        (new_order_id, item['product_id'], 1, item['price'])
                    )
                
                conn.commit() 
                successful_orders += 1
                
            except Exception as inner_e:
                print(f"Data blocked! The error is: {inner_e}") 
                conn.rollback() 
                continue
        
        print(f"✅ Successfully saved {successful_orders} orders and their items to the database!")
        
    except Exception as outer_e:
        print(f"❌ Major Pipeline Error: {outer_e}")
    finally:
        cur.close()
        conn.close()

def load_behavioral_events():
    print("--- Loading Behavioral Events to MongoDB ---")
    try:
        # 1. Load a sample of the electronics events
        # Note: Replace with your actual filename (e.g., '2019-Oct.csv')
        df = pd.read_csv('electronics_events.csv', nrows=5000)
        
        # 2. Convert to dictionary for Mongo
        records = df.to_dict('records')
        
        # 3. Connect and Insert
        uri = "mongodb+srv://myleszero5_db_user:ACS_Project2026@cluster0.3xd4wo3.mongodb.net/"
        client = MongoClient(uri, tlsCAFile=certifi.where())
        db = client['ecommerce_hybrid']
        
        db.user_activity.insert_many(records)
        
        print(f"✅ Successfully loaded {len(records)} behavioral events to MongoDB!")
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB Behavioral Load Failed: {e}")

def load_inventory_to_postgres():
    print("--- Loading Inventory to PostgreSQL ---")
    try:
        # 1. Load the products CSV
        products_df = pd.read_csv('olist_products_dataset.csv')
        
        # 2. Get unique product IDs to avoid duplicates
        unique_products = products_df['product_id'].unique()
        
        # 3. Connect to Postgres
        conn = psycopg2.connect(dbname="ecommerce_hybrid", user="myles", host="localhost")
        cur = conn.cursor()
        
        # 4. Insert into the inventory table
        for pid in unique_products:
            # We use ON CONFLICT DO NOTHING just in case you run this twice
            cur.execute(
                """
                INSERT INTO inventory (product_id) 
                VALUES (%s) 
                ON CONFLICT (product_id) DO NOTHING
                """,
                (pid,)
            )
            
        conn.commit()
        print(f"✅ Successfully loaded {len(unique_products)} products to Postgres Inventory!")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Inventory Load Failed: {e}")

if __name__ == "__main__":
    test_connections()
    load_products_to_mongo()
    load_users_to_postgres() #parent table loaded first
    load_orders_and_items()  #parent table loaded first
    load_behavioral_events() #child loaded last safely 
    load_inventory_to_postgres()
    
