import psycopg2
from pymongo import MongoClient
import certifi

def run_hybrid_business_intelligence():
    print("\n--- Running Hybrid Polyglot Query ---")
    print("Fetching financial aggregates from PostgreSQL (Olist Dataset)...")
    print("Fetching behavioral aggregates from MongoDB Atlas (Electronics Dataset)...")
    print("Bridging disparate ID schemas in application layer...\n")

    # 1. Fetch Top 5 Products by Revenue from PostgreSQL
    pg_conn = psycopg2.connect(dbname="ecommerce_hybrid", user="myles", host="localhost")
    cur = pg_conn.cursor()
    cur.execute("""
        SELECT product_id, SUM(price_at_purchase * quantity) as total_revenue
        FROM order_items
        GROUP BY product_id
        ORDER BY total_revenue DESC
        LIMIT 5;
    """)
    pg_data = cur.fetchall() # Returns list of tuples
    cur.close()
    pg_conn.close()

    # 2. Fetch Top 5 Products by Views from MongoDB
    uri = "mongodb+srv://myleszero5_db_user:ACS_Project2026@cluster0.3xd4wo3.mongodb.net/"
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client['ecommerce_hybrid']
    
    pipeline = [
        {"$group": {"_id": "$product_id", "total_views": {"$sum": 1}}},
        {"$sort": {"total_views": -1}},
        {"$limit": 5}
    ]
    mongo_data = list(db.user_activity.aggregate(pipeline)) # Returns list of dicts
    client.close()


    # 3. The "Data Bridge" Merge
    # Resolving the "Mismatched ID" problem (32-character hexadecimal UUIDs vs. 18-digit numeric IDs).

    print(f"{'SQL PRODUCT ID (OLIST)':<35} | {'NOSQL PRODUCT ID (EVENTS)':<25} | {'VIEWS':<6} | {'REVENUE':<10} | {'REV/VIEW'}")
    print("-" * 105)
    
    # Zip the top 5 from both databases together row-by-row
    for i in range(min(len(pg_data), len(mongo_data))):
        pg_prod_id = pg_data[i][0]
        revenue = float(pg_data[i][1])
        
        mongo_prod_id = str(mongo_data[i]['_id'])
        views = mongo_data[i]['total_views']
        
        rev_per_view = revenue / views
        
        print(f"{pg_prod_id:<35} | {mongo_prod_id:<25} | {views:<6} | ${revenue:<9.2f} | ${rev_per_view:.2f}")
            
    print("-" * 105)

# --- Database Connection Setup ---
def get_postgres_connection():
    return psycopg2.connect(dbname="ecommerce_hybrid", user="myles", host="localhost")

def get_mongo_connection():
    # Make sure to import certifi if you need it for Atlas TLS
    uri = "mongodb+srv://myleszero5_db_user:ACS_Project2026@cluster0.3xd4wo3.mongodb.net/"
    client = MongoClient(uri, tlsCAFile=certifi.where()) # 
    return client['ecommerce_hybrid']

# --- Core CRUD Functions ---
def view_user_history():
    print("\n--- View User Order History ---")
    user_email = input("Enter user email (e.g., test@example.com): ")
    
    conn = get_postgres_connection()
    cur = conn.cursor()
    
    try:
        # Query joining users, orders, and order_items
        # Notice we do NOT query a 'Product' table, we rely strictly on the items mapping
        cur.execute("""
            SELECT o.order_id, o.status, COUNT(oi.product_id) as total_items
            FROM users u
            JOIN orders o ON u.user_id = o.user_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE u.email = %s
            GROUP BY o.order_id, o.status;
        """, (user_email,))
        
        results = cur.fetchall()
        
        if not results:
            print("No orders found for this user.")
        else:
            print(f"\nOrder History for {user_email}:")
            for row in results:
                print(f"Order ID: {row[0]} | Status: {row[1]} | Total Items: {row[2]}")
                
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

# --- Main Interactive Menu ---
def main():
    while True:
        print("\n" + "="*40)
        print("ACS575 Hybrid E-Commerce Prototype")
        print("="*40)
        print("1. [Read] View a User's Order History")
        print("2. [Advanced] Run Analytical Queries")
        print("3. [Polyglot] Run Hybrid Business Intelligence")
        print("4. Exit")
        print("="*40)
        
        choice = input("Select an option (1-4): ")
        
        if choice == '1':
            view_user_history()
        elif choice == '2':
            run_analytical_queries()
        elif choice == '3':
            run_hybrid_business_intelligence()
        elif choice == '4':
            print("\nExiting prototype. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 4.")

def run_analytical_queries():
    print("\n" + "="*40)
    print("--- Advanced Analytical Reports (OLAP) ---")
    print("1. Financial Aggregation (PostgreSQL)")
    print("2. User Behavior Trends (MongoDB)")
    print("="*40)
    
    sub_choice = input("Select a report (1-2): ")
    
    if sub_choice == '1':
        print("\nCalculating total revenue and order volume by status...")
        conn = get_postgres_connection()
        cur = conn.cursor()
        try:
            # SQL Aggregation: Grouping by status, summing revenue, formatting output
            cur.execute("""
                SELECT o.status, COUNT(DISTINCT o.order_id) as total_orders, SUM(oi.price_at_purchase) as total_revenue
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY o.status
                ORDER BY total_revenue DESC;
            """)
            results = cur.fetchall()
            
            print(f"\n{'STATUS':<15} | {'TOTAL ORDERS':<15} | {'TOTAL REVENUE':<15}")
            print("-" * 50)
            for row in results:
                revenue = f"${row[2]:,.2f}" if row[2] else "$0.00"
                print(f"{row[0]:<15} | {row[1]:<15} | {revenue:<15}")
                
        except Exception as e:
            print(f"Postgres Error: {e}")
        finally:
            cur.close()
            conn.close()
            
    elif sub_choice == '2':
        print("\nAnalyzing high-velocity behavioral events in MongoDB Atlas...")
        mongo_db = get_mongo_connection()
        collection = mongo_db['user_activity']
        try:
            # MongoDB Aggregation Pipeline: Match views, group by product, count, sort, limit top 5
            pipeline = [
                
                {"$group": {"_id": "$product_id", "view_count": {"$sum": 1}}},
                {"$sort": {"view_count": -1}},
                {"$limit": 5}
            ]
            results = collection.aggregate(pipeline)
            
            print(f"\n{'PRODUCT ID':<20} | {'TOTAL VIEWS':<15}")
            print("-" * 40)
            for doc in results:
                print(f"{str(doc['_id']):<20} | {doc['view_count']:<15}")
                
        except Exception as e:
            print(f"MongoDB Error: {e}")
    else:
        print("\nInvalid selection.")
if __name__ == "__main__":
    main()