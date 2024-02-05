from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Replace the URI with your own MongoDB connection string
mongo_uri = "mongodb+srv://atlarusent:p2EQnKPeoyN4Xaet@main.zwuqy9k.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)

database = client.get_database("DB")
collection = database.get_collection("Businesses")

# Route to get all collections in the connected database
@app.route('/')
def get_all_collections():
    try:
        # Retrieve all documents from the collection
        documents = list(collection.find())
        
        return jsonify({"data": documents})
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/<business_id>', methods=['GET'])
def get_company(business_id):
    try:
        document = collection.find_one({"businessID": business_id})
        
        if document:
            # Convert ObjectId to string for JSON serialization
            document['_id'] = str(document['_id'])
            return jsonify({"status": "success", "document": document})
        else:
            return jsonify({"status": "error", "message": f"Document not found for businessID: {business_id}"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Use environment variables for host and port
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host=host, port=port)
