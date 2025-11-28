from pymongo import MongoClient
from bson.objectid import ObjectId

def init_db():
    client = MongoClient('localhost', 27017)
    db = client.flask_database
    return db

def get_contacts(db):
    contacts_collection = db['contacts']
    # Retrieve all contacts as a list of dictionaries
    contacts = list(contacts_collection.find({}))
    return contacts

def get_contact_by_id(db, contact_id):
    contacts_collection = db['contacts']
    # Retrieve a single contact by its ID
    contact = contacts_collection.find_one({"_id": contact_id})
    return contact

def add_contact(db, name, phone, email, group_name):
    contacts_collection = db['contacts']
    # Insert a new contact into the collection
    contacts_collection.insert_one({
        "name": name,
        "phone": phone,
        "email": email,
        "group_name": group_name
    })

def edit_contact(db, contact_id, name, phone, email, group_name):
    contacts_collection = db['contacts']
    # Update an existing contact by its ID
    contacts_collection.update_one(
        {"_id": contact_id},
        {"$set": {
            "name": name,
            "phone": phone,
            "email": email,
            "group_name": group_name
        }}
    )

def delete_contact(db, contact_id):
    contacts_collection = db['contacts']
    # Delete a contact by its ID
    contacts_collection.delete_one({"_id": contact_id})

def delete_multiple_contacts(db, contact_ids):
    contacts_collection = db['contacts']
    # Delete multiple contacts by their IDs
    contacts_collection.delete_many({"_id": {"$in": contact_ids}})












