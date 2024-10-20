from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db  # Import the db object from models/__init__.py
from models.budget import Budget  # Assuming you have a budget in models.budget
from models.user import User
from models.investment import Investment
from flask_apscheduler import APScheduler
from stock_api import get_stock_price #import the stock price function
from models import db, Investment

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SESSION_PERMANENT'] = False
app.config['SECRET_KEY'] = 'xuYzdGAVupa00wAqchtpGb0D0NMjsHIy'  # Needed for session management

# Initialize the database with the app
db.init_app(app)

# Initialize Flask extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirects to login page if not logged in

# Load the user from the database by ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Route to add a new budget expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json  # Get the data sent with POST request (JSON format)
    new_expense = Budget(category=data['category'], amount=data['amount'])  # Create a new budget entry
    db.session.add(new_expense)  # Add the new entry to the database session
    db.session.commit()  # Commit (save) the changes to the database
    return jsonify({"message": "Expense added successfully", "expense": new_expense.to_dict()}), 201

# Route to get all expenses
@app.route('/expenses', methods=['GET'])
@login_required
def get_expenses():
    expenses = Budget.query.all()  # Query all budget entries from the database
    return jsonify([expense.to_dict() for expense in expenses]), 200  # Return the expenses as a JSON array

# PUT: Update an expense
@app.route('/update_expense/<int:id>', methods=['PUT'])
def update_expense(id):
    data = request.get_json()  # Get the incoming JSON data from the request body
    expense = Budget.query.get(id)  # Find the expense by id

    if not expense:
        return jsonify({"message": "Expense not found"}), 404
    
    # Update the expense fields
    expense.category = data.get('category', expense.category)
    expense.amount = data.get('amount', expense.amount)

    db.session.commit()  # Save the changes to the database

    return jsonify({"message": "Expense updated successfully", "expense": expense.to_dict()}), 200

# DELETE: Delete an expense
@app.route('/delete_expense/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Budget.query.get(id)  # Find the expense by id

    if not expense:
        return jsonify({"message": "Expense not found"}), 404
    
    db.session.delete(expense)
    db.session.commit()  # Save the changes to the database

    return jsonify({"message": "Expense deleted successfully"}), 200

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 400

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    return jsonify({"message": "Register page"}), 200

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200




@app.route('/add_investment', methods=['POST'])
#@login_required  # user must be logged in
def add_investment():
    print("one")
    data = request.get_json()  # Get the incoming JSON data
    print(data)
    stock_symbol = data['investment_type']  # Stock Symbol like "NFLX"
    amount_invested = data['amount_invested']

    print(current_user)

    # Create a new investment for the logged-in user
    new_investment = Investment(
        investment_type=stock_symbol,
        amount_invested=amount_invested,
        user_id=current_user.id
    )

    db.session.add(new_investment)  # Add to the session
    db.session.commit()  # Save to the database
    return jsonify({"message": "Investment added successfully", "investment": new_investment.to_dict()}), 201


# Route to update an investment
@app.route('/update_investment/<int:id>', methods=['PUT'])
@login_required
def update_investment(id):
    data = request.get_json()
    investment = Investment.query.get(id)

    if not investment or investment.user_id != current_user.id:
        return jsonify({"message": "Investment not found"}), 404

    investment.investment_type = data.get('investment_type', investment.investment_type)
    investment.current_value = data.get('current_value', investment.current_value)
    db.session.commit()
    return jsonify({"message": "Investment updated successfully", "investment": investment.to_dict()}), 200

# Route to get investments for the current user
@app.route('/investments', methods=['GET'])
@login_required
def get_investments():
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    return jsonify([investment.to_dict() for investment in investments]), 200




# PUT: Update the current value of an investment
@app.route('/update_investment_value/<int:id>', methods=['PUT'])
@login_required
def update_investment_value(id):
    data = request.get_json()  # Get the incoming JSON data from the request body
    investment = Investment.query.get(id)  # Find the investment by id

    if not investment:
        return jsonify({"message": "Investment not found"}), 404

    # Only allow updating if the current user owns this investment
    if investment.user_id != current_user.id:
        return jsonify({"message": "Not authorized to update this investment"}), 403

    # Update the current value of the investment
    investment.current_value = data.get('current_value', investment.current_value)

    db.session.commit()  # Save the changes to the database

    return jsonify({"message": "Investment updated successfully", "investment": investment.to_dict()}), 200

# Configuration for scheduling jobs
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config)
scheduler = APScheduler()

# Function to update investments
def update_investment_values():
    with app.app_context():
        investments = Investment.query.all()
        for investment in investments:
            stock_symbol = investment.investment_type  # Assuming this field stores the stock symbol
            current_price = get_stock_price(stock_symbol)
            
            if current_price:
                investment.current_value = current_price * investment.amount_invested
                db.session.commit()

# Schedule the update task to run every 5 minutes
scheduler.add_job(id='update_investments', func=update_investment_values, trigger='interval', minutes=5)

# Initialize and start the scheduler
scheduler.init_app(app)
scheduler.start()

@app.route('/test_post', methods=['POST'])
def test_post():
    return jsonify({"message": "POST request received successfully!"}), 200




if __name__ == '__main__':
    # Create the tables if they don't exist
    with app.app_context():
        db.create_all()  # This will create the tables for all models
    app.run(debug=True)