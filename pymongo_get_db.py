from pymongo import MongoClient
from pymongo.server_api import ServerApi
from api_key import uri

def get_database():
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
   # Get the database
    dbname = get_database()