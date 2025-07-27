#!/usr/bin/env python3
"""
Project Pravaah - Firestore Database Seeding Script
===================================================
Seeds the 'project-pravaah' database with JSON data
"""

import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
import json
import os

# --- SETUP ---
# Use Application Default Credentials which are automatically available in Cloud Shell.
# This handles authentication securely.
cred = credentials.ApplicationDefault()

# Initialize the Firebase Admin SDK with the correct GCP project ID
# The database name 'project-pravaah' will be accessed within this project
firebase_admin.initialize_app(cred, {
    'projectId': 'stable-sign-454210-i0',  # Your actual GCP project ID
})

# Get a client to our Firestore database
# Connect directly to the 'project-pravaah' database using google-cloud-firestore
print("🔗 Connecting to database 'project-pravaah' in project 'stable-sign-454210-i0'...")

try:
    # Use google-cloud-firestore client which supports named databases
    db = firestore.Client(
        project='stable-sign-454210-i0',
        database='project-pravaah'
    )
    
    # Test the connection with a simple operation
    test_collection = db.collection('_connection_test')
    print("✅ Firebase Initialized Successfully. Connected to project: stable-sign-454210-i0, database: project-pravaah")
    
except Exception as e:
    print(f"❌ ERROR: Could not connect to database 'project-pravaah': {e}")
    print("💡 Make sure the database 'project-pravaah' exists in project 'stable-sign-454210-i0'")
    print("🔗 Check: https://console.firebase.google.com/project/stable-sign-454210-i0/firestore")
    raise e

# --- DATABASE SEEDING FUNCTION ---
def seed_collection(collection_name, file_name, id_field):
    """
    Seeds a Firestore collection by reading data from a local JSON file.
    """
    print(f"🌱 Seeding '{collection_name}' collection from {file_name}...")
    
    try:
        # Check if file exists
        if not os.path.exists(file_name):
            print(f"❌ ERROR: The file '{file_name}' was not found. Please make sure it's in the same directory.")
            return
        
        # Load JSON data
        with open(file_name, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        if not isinstance(data_list, list):
            print(f"❌ ERROR: {file_name} should contain a JSON array, got {type(data_list)}")
            return
        
        if not data_list:
            print(f"⚠️ WARNING: {file_name} is empty, skipping...")
            return
        
        # Use batch writes for efficiency
        batch = db.batch()
        successful_items = 0
        
        for item in data_list:
            try:
                # Ensure the item is a dictionary and has the required ID field
                if isinstance(item, dict) and id_field in item:
                    doc_id = str(item[id_field])  # Ensure doc_id is string
                    doc_ref = db.collection(collection_name).document(doc_id)
                    batch.set(doc_ref, item)
                    successful_items += 1
                else:
                    print(f"⚠️ Warning: Skipping invalid item in {file_name} (missing '{id_field}'): {item}")
            except Exception as item_error:
                print(f"⚠️ Warning: Error processing item in {file_name}: {item_error}")
                continue

        # Commit the batch
        if successful_items > 0:
            batch.commit()
            print(f"✅ Successfully seeded {successful_items} documents into '{collection_name}'.")
        else:
            print(f"❌ No valid documents found in {file_name} for collection '{collection_name}'.")
            
    except json.JSONDecodeError as json_error:
        print(f"❌ ERROR: Invalid JSON in '{file_name}': {json_error}")
    except Exception as e:
        print(f"❌ An error occurred while seeding '{collection_name}': {e}")

# --- EXECUTION ---
print("🚀 Starting Project Pravaah database seeding...")
print("=" * 60)

# List of files to check for
files_to_seed = [
    ("clients", "clients.json", "clientId"),
    ("users", "users.json", "userId"), 
    ("vehicles", "vehicles.json", "vehicleId"),
    ("drivers", "drivers.json", "driverId"),
    ("routes", "routes.json", "routeId"),
    ("journeys", "journeys.json", "journeyId")
]

# Check which files exist
existing_files = []
for collection, filename, id_field in files_to_seed:
    if os.path.exists(filename):
        existing_files.append((collection, filename, id_field))
        print(f"📁 Found: {filename}")
    else:
        print(f"⚠️ Missing: {filename}")

print(f"\n📊 Found {len(existing_files)} files to import")
print("=" * 60)

# Seed each existing file
for collection, filename, id_field in existing_files:
    seed_collection(collection, filename, id_field)
    print()  # Add spacing between collections

print("=" * 60)
print("🎉 Database seeding script finished!")
print(f"📈 Processed {len(existing_files)} collections")
print("🔗 Check the Firestore console at:")
print("   https://console.firebase.google.com/project/stable-sign-454210-i0/firestore")
print("=" * 60)
