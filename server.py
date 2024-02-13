from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Replace the URI with your own MongoDB connection string
mongo_uri = "mongodb+srv://atlarusent:p2EQnKPeoyN4Xaet@main.zwuqy9k.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)

database = client.get_database("DB")
collection = database.get_collection("Businesses")
referrals_collection = database.get_collection("Referrals")
billings_collection = database.get_collection("Billings")

###################################################################################
###################################################################################
################### ROUTES AVAILABLE FOR CLIENT AUTHENTICATION ####################
###################################################################################
###################################################################################

### REGISTER BUSINESS ###
@app.route('/register_business', methods=['POST'])
def register_business():
    user_id = request.json.get('userID')
    business_id = request.json.get('businessID')
    email = request.json.get('email')
    password = request.json.get('password')
    address = request.json.get('address')
    referral = request.json.get('referral')

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
    
    if referral and business_id:
        register_referral(referral, business_id)

    return jsonify({'message': 'Business registered successfully'})

### ADD TO REFERRAL LIST ###
def register_referral(referral_code, business_id):
    if not referral_code or not business_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on referralCode
    referrals_data = referrals_collection.find_one({'referralCode': referral_code})

    if not referrals_data:
        return jsonify({'error': 'Referral not found'}), 404

    # Update the referrals array in the document
    existing_referrals = referrals_data.get('referrals', [])
    existing_referrals.extend(business_id)

    # Remove duplicates by converting the list to a set and then back to a list
    unique_referrals = list(set(existing_referrals))

    # Update the document in the database
    referrals_collection.update_one({'referralCode': referral_code}, {'$set': {'referrals': unique_referrals}})

    return jsonify({'message': 'Referrals updated successfully'})

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

##############################################################################
##############################################################################
#################### ROUTES AVAILABLE FOR CLIENT SETTINGS ####################
##############################################################################
##############################################################################

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

###############################################################################
###############################################################################
#################### ROUTES AVAILABLE FOR CLIENT CUSTOMERS ####################
###############################################################################
###############################################################################
    
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

@app.route('/insert_review', methods=['POST'])
def insert_review():
    business_id = request.json.get('businessID')
    product_id = request.json.get('productID')
    new_review = request.json.get('newReview')

    if not business_id or not product_id or not new_review:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Find the product within the 'products' array
    products = business_data.get('products', [])

    for product in products:
        if product.get('productID') == product_id:
            # Add a new review to the 'review' array in the product
            product_reviews = product.get('review', [])
            product_reviews.append(new_review)

            # Update the document in the database
            collection.update_one({'businessID': business_id, 'products.productID': product_id},
                                             {'$set': {'products.$.review': product_reviews}})
            return jsonify({'message': 'Review inserted successfully'})

    return jsonify({'error': 'Product not found'}), 404

@app.route('/get_all_reviews', methods=['GET'])
def get_all_reviews():
    business_id = request.args.get('businessID')
    product_id = request.args.get('productID')

    if not business_id or not product_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Find the product within the 'products' array
    products = business_data.get('products', [])

    for product in products:
        if product.get('productID') == product_id:
            # Retrieve all reviews for the specified product
            product_reviews = product.get('review', [])
            return jsonify({'businessID': business_id, 'productID': product_id, 'reviews': product_reviews})

    return jsonify({'error': 'Product not found'}), 404

#####################################################################################
#####################################################################################
#################### ROUTES AVAILABLE FOR CLIENT PRODUCTS (CRUD) ####################
#####################################################################################
#####################################################################################

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

#####################################################################################
#####################################################################################
#################### ROUTES AVAILABLE FOR CLIENT SERVICES (CRUD) ####################
#####################################################################################
#####################################################################################

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

###################################################################################
###################################################################################
#################### ROUTES AVAILABLE FOR CLIENT ORDERS (CRUD) ####################
###################################################################################
###################################################################################

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

#############################################################################
#############################################################################
#################### ROUTES AVAILABLE FOR CLIENT COUPONS ####################
#############################################################################
#############################################################################

### INSERT COUPON ###
@app.route('/insert_coupon', methods=['POST'])
def insert_coupon():
    business_id = request.json.get('businessID')
    new_coupon = request.json.get('newCoupon')

    if not business_id or not new_coupon:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Add a new coupon to the 'coupons' array in the document
    coupons = business_data.get('coupons', [])
    coupons.append(new_coupon)

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'coupons': coupons}})

    return jsonify({'message': 'Coupon inserted successfully'})

### REMOVE COUPON ###
@app.route('/remove_coupon', methods=['DELETE'])
def remove_coupon():
    business_id = request.json.get('businessID')
    coupon_code = request.json.get('couponCode')

    if not business_id or not coupon_code:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Remove the coupon from the 'coupons' array in the document
    coupons = business_data.get('coupons', [])

    updated_coupons = [coupon for coupon in coupons if coupon.get('code') != coupon_code]

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'coupons': updated_coupons}})

    return jsonify({'message': 'Coupon removed successfully'})

### READ ALL COUPONS ###
@app.route('/get_all_coupons', methods=['GET'])
def get_all_coupons():
    business_id = request.args.get('businessID')

    if not business_id:
        return jsonify({'error': 'BusinessID parameter is missing'}), 400

    # Query the database to retrieve all coupons based on the provided businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    coupons = business_data.get('coupons', [])

    return jsonify({'businessID': business_id, 'coupons': coupons})

### UPDATE COUPONS ###
@app.route('/update_coupon', methods=['PUT'])
def update_coupon():
    business_id = request.json.get('businessID')
    coupon_code = request.json.get('couponCode')
    updated_values = request.json.get('updatedValues')

    if not business_id or not coupon_code or not updated_values:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Update specific values of the coupon in the 'coupons' array
    coupons = business_data.get('coupons', [])

    for coupon in coupons:
        if coupon.get('code') == coupon_code:
            for key, value in updated_values.items():
                coupon[key] = value

            # Update the document in the database
            collection.update_one({'businessID': business_id}, {'$set': {'coupons': coupons}})
            return jsonify({'message': 'Coupon updated successfully'})

    return jsonify({'error': 'Coupon not found'}), 404

############################################################################
############################################################################
#################### ROUTES AVAILABLE FOR CLIENT EVENTS ####################
############################################################################
############################################################################

### ADD EVENT ###
@app.route('/add_event', methods=['POST'])
def add_event():
    business_id = request.json.get('businessID')
    new_event = request.json.get('newEvent')

    if not business_id or not new_event:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Add a new event to the 'events' array in the document
    events = business_data.get('events', [])
    events.append(new_event)

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'events': events}})

    return jsonify({'message': 'Event added successfully'})

### UPDATE EVENT DETAILS ###
@app.route('/update_event', methods=['PUT'])
def update_event():
    business_id = request.json.get('businessID')
    event_id = request.json.get('eventID')
    updated_values = request.json.get('updatedValues')

    if not business_id or not event_id or not updated_values:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Update specific values of the event in the 'events' array
    events = business_data.get('events', [])

    for event in events:
        if event.get('eventID') == event_id:
            for key, value in updated_values.items():
                event[key] = value

            # Update the document in the database
            collection.update_one({'businessID': business_id}, {'$set': {'events': events}})
            return jsonify({'message': 'Event updated successfully'})

    return jsonify({'error': 'Event not found'}), 404

### GET ALL EVENTS ###
@app.route('/get_all_events', methods=['GET'])
def get_all_events():
    business_id = request.args.get('businessID')

    if not business_id:
        return jsonify({'error': 'BusinessID parameter is missing'}), 400

    # Query the database to retrieve all events based on the provided businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    events = business_data.get('events', [])

    return jsonify({'businessID': business_id, 'events': events})

### REMOVE EVENT ###
@app.route('/remove_event', methods=['DELETE'])
def remove_event():
    business_id = request.json.get('businessID')
    event_id = request.json.get('eventID')

    if not business_id or not event_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Remove the event from the 'events' array in the document
    events = business_data.get('events', [])

    updated_events = [event for event in events if event.get('eventID') != event_id]

    # Update the document in the database
    collection.update_one({'businessID': business_id}, {'$set': {'events': updated_events}})

    return jsonify({'message': 'Event removed successfully'})

#############################################################################
#############################################################################
#################### ROUTES AVAILABLE FOR PLATFORM ADMIN ####################
#############################################################################
#############################################################################

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
    
### ADD BUSINESS TO BE REFERRAL ###
@app.route('/add_referral', methods=['POST'])
def add_referral():
    business_id = request.json.get('businessID')

    if not business_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Check if the referral code already exists
    existing_referral = referrals_collection.find_one({'businessID': business_id})

    if existing_referral:
        return jsonify({'error': 'Referral already exists'}), 409

    # Insert a new document into the 'Referrals' collection with an empty 'referrals' array
    new_referral = {
        'businessID': business_id,
        'referralCode': business_id,
        'referrals': []
    }

    referrals_collection.insert_one(new_referral)

    return jsonify({'message': 'Referral added successfully'})

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

### GET ALL TAGS ###
@app.route('/get_all_ordered_tags', methods=['GET'])
def get_all_ordered_tags():
    # Query the database to retrieve all businesses and their ordered tags
    all_businesses_data = collection.find({}, {'_id': 0, 'businessID': 1, 'orderedTags': 1})

    ordered_tags_by_business = {}

    for business_data in all_businesses_data:
        business_id = business_data.get('businessID')
        ordered_tags = business_data.get('orderedTags', [])

        ordered_tags_by_business[business_id] = ordered_tags

    return jsonify({'orderedTagsByBusiness': ordered_tags_by_business})

### INSERTING NEW BUSINESS TO BILLING ###
@app.route('/insert_billing', methods=['POST'])
def insert_billing():
    business_id = request.json.get('businessID')

    if not business_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Check if a billing document already exists for the given businessID
    existing_billing = billings_collection.find_one({'businessID': business_id})

    if existing_billing:
        return jsonify({'error': 'Billing document already exists'}), 409

    # Insert a new document into the 'Billings' collection with an empty 'bills' array
    new_billing = {
        'businessID': business_id,
        'bills': [],
        'subscriptionLevel': ""
    }

    billings_collection.insert_one(new_billing)

    return jsonify({'message': 'Billing document inserted successfully'})

### ADD BILL TO BUSINESS ###
@app.route('/add_bill', methods=['POST'])
def add_bill():
    business_id = request.json.get('businessID')
    payment_status = request.json.get('paymentStatus')
    amount = request.json.get('amount')
    due = request.json.get('due')

    if not business_id or not payment_status or not amount or not due:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    billing_data = billings_collection.find_one({'businessID': business_id})

    if not billing_data:
        return jsonify({'error': 'Billing document not found'}), 404

    # Add a new bill to the 'bills' array in the document
    bills = billing_data.get('bills', [])
    new_bill = {
        'paymentStatus': payment_status,
        'amount': amount,
        'due': due
    }
    bills.append(new_bill)

    # Update the document in the database
    billings_collection.update_one({'businessID': business_id}, {'$set': {'bills': bills}})

    return jsonify({'message': 'Bill added successfully'})

### UPDATE BILL VALUES ###
@app.route('/update_bill', methods=['PUT'])
def update_bill():
    business_id = request.json.get('businessID')
    bill_index = request.json.get('billIndex')  # Index of the bill to be updated in the 'bills' array
    updated_values = request.json.get('updatedValues')  # Updated values for the bill

    if not business_id or bill_index is None or not updated_values:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    billing_data = billings_collection.find_one({'businessID': business_id})

    if not billing_data:
        return jsonify({'error': 'Billing document not found'}), 404

    # Update specific values of the bill in the 'bills' array
    bills = billing_data.get('bills', [])

    if 0 <= bill_index < len(bills):
        for key, value in updated_values.items():
            bills[bill_index][key] = value

        # Update the document in the database
        billings_collection.update_one({'businessID': business_id}, {'$set': {'bills': bills}})
        return jsonify({'message': 'Bill updated successfully'})
    else:
        return jsonify({'error': 'Invalid bill index'}), 400
    
### UPDATE BUSINESS BILLING ACTIVE STATUS ###
@app.route('/update_status', methods=['PUT'])
def update_status():
    business_id = request.json.get('businessID')
    new_status = request.json.get('status')

    if not business_id or not new_status:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    billing_data = billings_collection.find_one({'businessID': business_id})

    if not billing_data:
        return jsonify({'error': 'Billing document not found'}), 404

    # Update the 'status' field in the document
    billings_collection.update_one({'businessID': business_id}, {'$set': {'status': new_status}})

    return jsonify({'message': 'Status updated successfully'})

@app.route('/remove_review', methods=['DELETE'])
def remove_review():
    business_id = request.json.get('businessID')
    product_id = request.json.get('productID')
    review_id = request.json.get('reviewID')

    if not business_id or not product_id or not review_id:
        return jsonify({'error': 'Invalid request data'}), 400

    # Query the database to find the document based on businessID
    business_data = collection.find_one({'businessID': business_id})

    if not business_data:
        return jsonify({'error': 'Business not found'}), 404

    # Find the product within the 'products' array
    products = business_data.get('products', [])

    for product in products:
        if product.get('productID') == product_id:
            # Remove the specified review from the 'review' array in the product
            product_reviews = product.get('review', [])

            updated_reviews = [r for r in product_reviews if r.get('reviewID') != review_id]

            # Update the document in the database
            collection.update_one({'businessID': business_id, 'products.productID': product_id},
                                             {'$set': {'products.$.review': updated_reviews}})
            return jsonify({'message': 'Review removed successfully'})

    return jsonify({'error': 'Product not found'}), 404

#################################################################
#################################################################
#################### FUNCTIONS TO RUN SERVER ####################
#################################################################
#################################################################

if __name__ == '__main__':
    # Use environment variables for host and port
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host=host, port=port)
