from flask import Flask, jsonify, request
from http import HTTPStatus

app = Flask(__name__)

# In-memory contacts list
contacts = []

def validate_contact(contact):
    """Validate contact data."""
    required_fields = ['name', 'email', 'phone']
    if not all(field in contact for field in required_fields):
        return False, "Missing required fields: name, email, and phone are required"
    
    # Validate email format (basic validation)
    if '@' not in contact['email']:
        return False, "Invalid email format"
    
    # Validate phone number (basic validation)
    if not contact['phone'].replace('-', '').replace('+', '').isdigit():
        return False, "Invalid phone number format"
    
    return True, ""

@app.route('/')
def home():
    return "Welcome to the Hacktoberfest CRM!"

@app.route('/contacts', methods=['GET'])
def get_contacts():
    """Get the list of contacts with optional search parameters."""
    search_term = request.args.get('search', '').lower()
    
    if search_term:
        filtered_contacts = [
            contact for contact in contacts
            if search_term in contact.get('name', '').lower() or
               search_term in contact.get('email', '').lower() or
               search_term in contact.get('phone', '').lower()
        ]
        return jsonify(filtered_contacts)
    
    return jsonify(contacts)

@app.route('/contacts', methods=['POST'])
def add_contact():
    """Add a new contact with validation."""
    data = request.get_json()
    
    # Validate contact data
    is_valid, error_message = validate_contact(data)
    if not is_valid:
        return jsonify({'error': error_message}), HTTPStatus.BAD_REQUEST
    
    # Check for duplicate email
    if any(contact['email'] == data['email'] for contact in contacts):
        return jsonify({'error': 'Email already exists'}), HTTPStatus.CONFLICT
    
    contacts.append(data)
    return jsonify({'message': 'Contact added successfully!', 'contact': data}), HTTPStatus.CREATED

@app.route('/contacts/<email>', methods=['PUT'])
def update_contact(email):
    """Update an existing contact."""
    data = request.get_json()
    
    # Validate contact data
    is_valid, error_message = validate_contact(data)
    if not is_valid:
        return jsonify({'error': error_message}), HTTPStatus.BAD_REQUEST
    
    for i, contact in enumerate(contacts):
        if contact['email'] == email:
            # Don't allow email updates to prevent duplicates
            data['email'] = email
            contacts[i] = data
            return jsonify({'message': 'Contact updated successfully!', 'contact': data})
    
    return jsonify({'error': 'Contact not found'}), HTTPStatus.NOT_FOUND

@app.route('/contacts/<email>', methods=['DELETE'])
def delete_contact(email):
    """Delete a contact."""
    for i, contact in enumerate(contacts):
        if contact['email'] == email:
            deleted_contact = contacts.pop(i)
            return jsonify({
                'message': 'Contact deleted successfully!',
                'contact': deleted_contact
            })
    
    return jsonify({'error': 'Contact not found'}), HTTPStatus.NOT_FOUND

if __name__ == '__main__':
    app.run(debug=True)
