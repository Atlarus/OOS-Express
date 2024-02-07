from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Replace the URI with your own MongoDB connection string
mongo_uri = "mongodb+srv://atlarusent:p2EQnKPeoyN4Xaet@main.zwuqy9k.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)

database = client.get_database("DB")
collection = database.get_collection("Businesses")

######################################################
######################################################
##### ROUTES AVAILABLE FOR CLIENT AUTHENTICATION #####
######################################################
######################################################

### REGISTER BUSINESS ###
@app.route('/register_business', methods=['POST'])
def register_business():
    user_id = request.json.get('userID')
    business_id = request.json.get('businessID')
    email = request.json.get('email')
    password = request.json.get('password')
    address = request.json.get('address')

    if not user_id or not business_id or not email or not password or not address:
        return jsonify({'error': 'Invalid request data'}), 400

    # Check if the businessID or email is already registered
    existing_business = collection.find_one({
        '$or': [
            {'businessID': business_id},
            {'email': email}
        ]
    })

    if existing_business:
        return jsonify({'error': 'Business or email already registered'}), 409

    # Insert the new business into the 'Businesses' collection
    new_business = {
        'userID': user_id,
        'businessID': business_id,
        'email': email,
        'password': password,
        'address': address,
        'products': [],
        'services': [],
        'orders': []
    }

    collection.insert_one(new_business)

    return jsonify({'message': 'Business registered successfully'})

### LOGIN BUSINESS ###
@app.route('/business_login', methods=['POST'])
def business_login():
    user_id = request.json.get('userID')
    password = request.json.get('password')

    if not user_id or not password:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the business based on userID and password
    business_data = collection.find_one({'userID': user_id, 'password': password})

    if not business_data:
        return jsonify({'error': 'Invalid userID or password'}), 401

    # You may want to return additional information such as businessID, email, etc.
    response_data = {
        'message': 'Login successful',
        'businessID': business_data['businessID'],
        'email': business_data['email']
        # Add more fields as needed
    }

    return jsonify(response_data)

################################################
################################################
##### ROUTES AVAILABLE FOR CLIENT SETTINGS #####
################################################
################################################

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

### UPDATE EMAIL ###
@app.route('/update_email', methods=['PUT'])
def update_email():
    business_id = request.json.get('businessID')
    new_email = request.json.get('newEmail')

    if not business_id or not new_email:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Check if the new email is already registered by another business
    existing_business = collection.find_one({'email': new_email})

    if existing_business:
        return jsonify({'error': 'Email already registered by another business'}), 409

    # Update the email in the document
    collection.update_one({'businessID': business_id}, {'$set': {'email': new_email}})

    return jsonify({'message': 'Email updated successfully'})

### UPDATE ADDRESS ###
@app.route('/update_address', methods=['PUT'])
def update_address():
    business_id = request.json.get('businessID')
    new_address = request.json.get('newAddress')

    if not business_id or not new_address:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Update the address in the document
    collection.update_one({'businessID': business_id}, {'$set': {'address': new_address}})

    return jsonify({'message': 'Address updated successfully'})

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

#####################################################
#####################################################
##### ROUTES AVAILABLE FOR CLIENT ORDERS (CRUD) #####
#####################################################
#####################################################

### INSERT ORDER ###
@app.route('/insert_order', methods=['POST'])
def insert_order():
    business_id = request.json.get('businessID')
    order_data = request.json.get('order')

    if not business_id or not order_data:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Insert the new order into the 'orders' array
    orders = business_data.get('orders', [])
    orders.append(order_data)

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'orders': orders}})

    return jsonify({'message': 'Order inserted successfully'})

### RETRIEVE ORDERS ###
@app.route('/get_all_orders', methods=['GET'])
def get_all_orders():
    business_id = request.args.get('businessID')

    if not business_id:
        return jsonify({'error': 'BusinessID parameter is missing'}), 400

    # Query the database to retrieve all orders based on the provided businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    orders = business_data.get('orders', [])

    return jsonify({'businessID': business_id, 'orders': orders})

### UPDATE ORDER ###
@app.route('/update_order', methods=['PUT'])
def update_order():
    business_id = request.json.get('businessID')
    order_id = request.json.get('orderID')
    updated_order_data = request.json.get('updatedOrder')

    if not business_id or not order_id or not updated_order_data:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Update specific fields of the order within the 'orders' array
    orders = business_data.get('orders', [])

    for order in orders:
        if order.get('orderID') == order_id:
            for key, value in updated_order_data.items():
                order[key] = value

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'orders': orders}})

    return jsonify({'message': 'Order updated successfully'})

### REMOVE ORDER ###
@app.route('/remove_order', methods=['DELETE'])
def remove_order():
    business_id = request.json.get('businessID')
    order_id = request.json.get('orderID')

    if not business_id or not order_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Remove the order from the 'orders' array
    orders = business_data.get('orders', [])

    updated_orders = [order for order in orders if order.get('orderID') != order_id]

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'orders': updated_orders}})

    return jsonify({'message': 'Order removed successfully'})

###############################################
###############################################
##### ROUTES AVAILABLE FOR PLATFORM ADMIN #####
###############################################
###############################################

### REMOVE BUSINESS ###
@app.route('/remove_business', methods=['DELETE'])
def remove_business():
    business_id = request.json.get('businessID')

    if not business_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find and remove the document based on businessID
    result = collection.delete_one({'businessID': business_id})

    if result.deleted_count == 0:
        return jsonify({'error': 'Business not found'}), 404
    else:
        return jsonify({'message': 'Business removed successfully'})

### STORE TAGS ###
@app.route('/store_ordered_tags', methods=['POST'])
def store_ordered_tags():
    business_id = request.json.get('businessID')
    ordered_tags = request.json.get('orderedTags')

    if not business_id or not ordered_tags:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Store the ordered tags in the document
    existing_ordered_tags = business_data.get('orderedTags', [])
    existing_ordered_tags.extend(ordered_tags)

    # Remove duplicates by converting the list to a set and then back to a list
    unique_ordered_tags = list(set(existing_ordered_tags))

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'orderedTags': unique_ordered_tags}})

    return jsonify({'message': 'Ordered tags stored successfully'})

if __name__ == '__main__':
    # Use environment variables for host and port
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host=host, port=port)
