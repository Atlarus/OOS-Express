from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Replace the URI with your own MongoDB connection string
mongo_uri = "mongodb+srv://atlarusent:p2EQnKPeoyN4Xaet@main.zwuqy9k.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)

database = client.get_database("DB")
collection = database.get_collection("Businesses")

#################################################
#################################################
##### ROUTES AVAILABLE FOR CLIENT SETTINGS #####
#################################################
#################################################

### UPDATE PASSWORD ###
@app.route('/update_password', methods=['PUT'])
def update_password():
    business_id = request.json.get('businessID')
    new_password = request.json.get('newPassword')

    if not business_id or not new_password:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Update the password in the document
    collection.update_one({'businessID': business_id}, {'$set': {'password': new_password}})

    return jsonify({'message': 'Password updated successfully'})

#################################################
#################################################
##### ROUTES AVAILABLE FOR CLIENT CUSTOMERS #####
#################################################
#################################################
    
@app.route('/get_products_services', methods=['GET'])
def get_products_services():
    business_id = request.args.get('businessID')

    if not business_id:
        return jsonify({'error': 'BusinessID parameter is missing'}), 400

    # Query the database to retrieve products and services based on the provided businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    products = business_data.get('products', [])
    services = business_data.get('services', [])

    result = {
        'businessID': business_id,
        'products': products,
        'services': services
    }

    return jsonify(result)

#######################################################
#######################################################
##### ROUTES AVAILABLE FOR CLIENT PRODUCTS (CRUD) #####
#######################################################
#######################################################

### INSERT PRODUCT ###
@app.route('/insert_product', methods=['POST'])
def insert_product():
    business_id = request.json.get('businessID')
    product_data = request.json.get('product')

    if not business_id or not product_data:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Insert the new product into the 'products' array
    products = business_data.get('products', [])
    products.append(product_data)

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'products': products}})

    return jsonify({'message': 'Product inserted successfully'})

### READ PRODUCTS ###
@app.route('/get_all_products', methods=['GET'])
def get_all_products():
    business_id = request.args.get('businessID')

    if not business_id:
        return jsonify({'error': 'BusinessID parameter is missing'}), 400

    # Query the database to retrieve all products based on the provided businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    products = business_data.get('products', [])

    return jsonify({'businessID': business_id, 'products': products})

### UPDATE PRODUCT ###
@app.route('/update_product', methods=['PUT'])
def update_product():
    business_id = request.json.get('businessID')
    product_id = request.json.get('productID')
    updated_product_data = request.json.get('updatedProduct')

    if not business_id or not product_id or not updated_product_data:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Update specific fields of the product within the 'products' array
    products = business_data.get('products', [])

    for product in products:
        if product.get('productID') == product_id:
            for key, value in updated_product_data.items():
                product[key] = value

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'products': products}})

    return jsonify({'message': 'Product updated successfully'})

### REMOVE PRODUCT ###
@app.route('/remove_product', methods=['DELETE'])
def remove_product():
    business_id = request.json.get('businessID')
    product_id = request.json.get('productID')

    if not business_id or not product_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Remove the product from the 'products' array
    products = business_data.get('products', [])

    updated_products = [product for product in products if product.get('productID') != product_id]

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'products': updated_products}})

    return jsonify({'message': 'Product removed successfully'})

#######################################################
#######################################################
##### ROUTES AVAILABLE FOR CLIENT SERVICES (CRUD) #####
#######################################################
#######################################################

### INSERT SERVICE ###
@app.route('/insert_service', methods=['POST'])
def insert_service():
    business_id = request.json.get('businessID')
    service_data = request.json.get('service')

    if not business_id or not service_data:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Insert the new service into the 'services' array
    services = business_data.get('services', [])
    services.append(service_data)

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'services': services}})

    return jsonify({'message': 'Service inserted successfully'})

### READ SERVICES ###
@app.route('/get_all_services', methods=['GET'])
def get_all_services():
    business_id = request.args.get('businessID')

    if not business_id:
        return jsonify({'error': 'BusinessID parameter is missing'}), 400

    # Query the database to retrieve all services based on the provided businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    services = business_data.get('services', [])

    return jsonify({'businessID': business_id, 'services': services})

### UPDATE SERVICE ###
@app.route('/update_service', methods=['PUT'])
def update_service():
    business_id = request.json.get('businessID')
    service_id = request.json.get('serviceID')
    updated_service_data = request.json.get('updatedService')

    if not business_id or not service_id or not updated_service_data:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Update specific fields of the service within the 'services' array
    services = business_data.get('services', [])

    for service in services:
        if service.get('serviceID') == service_id:
            for key, value in updated_service_data.items():
                service[key] = value

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'services': services}})

    return jsonify({'message': 'Service updated successfully'})

### REMOVE SERVICE ###
@app.route('/remove_service', methods=['DELETE'])
def remove_service():
    business_id = request.json.get('businessID')
    service_id = request.json.get('serviceID')

    if not business_id or not service_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Remove the service from the 'services' array
    services = business_data.get('services', [])

    updated_services = [service for service in services if service.get('serviceID') != service_id]

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'services': updated_services}})

    return jsonify({'message': 'Service removed successfully'})

if __name__ == '__main__':
    # Use environment variables for host and port
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host=host, port=port)
