from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
import pandas as pd
import io
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key in production

# Define the path to the file where user registrations will be stored
USER_DATA_FILE = 'user_data.json'

# Load existing user registrations from the file if it exists
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'r') as file:
        registered_users = json.load(file)
else:
    registered_users = {}  # Initialize an empty dictionary if the file doesn't exist

# Save user registrations to the file whenever a new registration is made
def save_user_data():
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(registered_users, file)

# Sample database (you can replace this with your own database connection)
database = []

# Load data from the database when the application starts
def load_data():
    global database
    # Add your code to load data from the database here
    # For demonstration purposes, let's initialize the database with some sample data
    database = [
        {'Date': '2024-01-01', 'Product Name': 'Product 1', 'Quantity': 10, 'IMEI number': '123456789012345', 'Purchase': 100, 'Sale': 120, 'Expense': 10, 'Profit': 20, 'Total Profit': 200},
        {'Date': '2024-01-02', 'Product Name': 'Product 2', 'Quantity': 8, 'IMEI number': '987654321098765', 'Purchase': 90, 'Sale': 110, 'Expense': 8, 'Profit': 12, 'Total Profit': 96},
        # Add more sample data as needed
    ]

# Load data from the database when the application starts
load_data()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in registered_users and registered_users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            # Clear form data on failed login attempt
            return render_template('login.html', error='Invalid username or password.')
    else:
        # Clear form data when displaying the login page
        return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.clear()  # Clear session data completely
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in registered_users:
            registered_users[username] = password
            save_user_data()  # Save the updated user registrations
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Username already exists.')
    return render_template('register.html')

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', database=database)
    else:
        return redirect(url_for('login'))
    
@app.route('/add_entry', methods=['POST'])
def add_entry():
    date = request.form['date']
    product_name = request.form['product_name']
    quantity = int(request.form['quantity'])
    imei_number = request.form['imei_number']
    purchase = float(request.form['purchase'])
    sale = float(request.form['sale'])
    expense = float(request.form['expense'])
    purchaser_name = request.form['purchaser_name']  # New field
    purchaser_phone = request.form['purchaser_phone']  # New field
    seller_name = request.form['seller_name']  # New field
    seller_phone = request.form['seller_phone']  # New field
    remarks = request.form['remarks']  # New field

    profit = sale - purchase
    total_profit = profit - expense

    entry = {
        'Date': date,
        'Product Name': product_name,
        'Quantity': quantity,
        'IMEI number': imei_number,
        'Purchase': purchase,
        'Sale': sale,
        'Expense': expense,
        'Profit': profit,
        'Total Profit': total_profit,
        'Name of Purchaser': purchaser_name,  # New field
        'Purchaser Phone No': purchaser_phone,  # New field
        'Name of Seller': seller_name,  # New field
        'Seller Phone No': seller_phone,  # New field
        'Remarks': remarks  # New field
    }

    database.append(entry)

    return redirect(url_for('index'))

@app.route('/import_data', methods=['POST'])
def import_data():
    file = request.files['file']
    if file:
        content = file.read()
        df = pd.read_excel(io.BytesIO(content))
        # Clear existing database before importing new data
        database.clear()
        for _, row in df.iterrows():
            entry = row.to_dict()
            database.append(entry)
            # Print a sample row to check IMEI number data
            print(entry)
    return redirect(url_for('index'))

@app.route('/delete_entry/<int:index>')
def delete_entry(index):
    del database[index]
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        result = [entry for entry in database if start_date <= entry['Date'] <= end_date]
    else:
        result = database
    
    return jsonify(result)

# Add a route for deleting all entries
@app.route('/delete_all', methods=['POST'])
def delete_all():
    database.clear()
    return redirect(url_for('index'))


@app.route('/download_report')
def download_report():
    df = pd.DataFrame(database)
    df.to_excel('report.xlsx', index=False)  # Save as Excel file
    return send_file('report.xlsx', as_attachment=True)

@app.route('/print_report')
def print_report():
    # Generate report in HTML format for printing
    # For simplicity, we'll render the report directly in the browser
    return render_template('print_report.html', database=database)


