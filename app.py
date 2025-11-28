from flask import Flask, render_template, request, redirect, url_for
from join import init_db, get_contacts, add_contact, edit_contact, delete_contact, get_contact_by_id, delete_multiple_contacts
from bson.objectid import ObjectId  # Import ObjectId for MongoDB ID handling

app = Flask(__name__, template_folder='.')
db = init_db()  # Initialize MongoDB

@app.route('/')
def index():
    contacts = get_contacts(db)
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['GET', 'POST'])
def add_contact_route():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        group_name = request.form['group_name']
        add_contact(db, name, phone, email, group_name)
        return redirect(url_for('index'))
    return render_template('form.html')

@app.route('/edit/<string:contact_id>', methods=['GET', 'POST'])
def edit_contact_route(contact_id):
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        group_name = request.form['group_name']
        edit_contact(db, ObjectId(contact_id), name, phone, email, group_name)
        return redirect(url_for('index'))

    contact = get_contact_by_id(db, ObjectId(contact_id))
    if contact:
        return render_template('edit.html', contact=contact)
    else:
        return "Contact not found", 404

@app.route('/delete/<string:contact_id>', methods=['GET'])
def delete_contact_route(contact_id):
    delete_contact(db, ObjectId(contact_id))
    return redirect(url_for('index'))

@app.route('/delete_multiple', methods=['POST'])
def delete_multiple_contacts_route():
    contact_ids = request.form.getlist('contact_ids')
    if contact_ids:
        object_ids = [ObjectId(id) for id in contact_ids]
        delete_multiple_contacts(db, object_ids)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)











