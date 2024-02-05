from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Replace the URI with your own MongoDB connection string
mongo_uri = "mongodb+srv://atlarusent:p2EQnKPeoyN4Xaet@main.zwuqy9k.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)

# Route to get all collections in the connected database
@app.route('/')
def get_all_collections():
    try:
        database = client.get_database("DB")
        collection = database.get_collection("Businesses")
        
        # Retrieve all documents from the collection
        documents = list(collection.find())
        
        return jsonify({"data": documents})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # Use environment variables for host and port
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host=host, port=port)
