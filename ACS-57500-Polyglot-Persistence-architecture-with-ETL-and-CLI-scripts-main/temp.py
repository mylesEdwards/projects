# Run this in a new temporary python file or at the bottom of yours
from pymongo import MongoClient
import certifi

uri = "mongodb+srv://myleszero5_db_user:ACS_Project2026@cluster0.3xd4wo3.mongodb.net/"
client = MongoClient(uri, tlsCAFile=certifi.where())

print("Databases on this cluster:")
print(client.list_database_names())
client.close()