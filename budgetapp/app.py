from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sql@123",
    database="budgetapp"
)

cursor = db.cursor()

# -------- CREATE TABLES IF NOT EXIST --------

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100),
    amount DECIMAL(10,2),
    description VARCHAR(255),
    date DATE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS budget (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_budget DECIMAL(10,2)
)
""")

# Insert default budget if table is empty
cursor.execute("SELECT COUNT(*) FROM budget")
count = cursor.fetchone()[0]

if count == 0:
    cursor.execute("INSERT INTO budget(total_budget) VALUES (50000)")
    db.commit()

# --------------------------------------------

@app.route('/')
def dashboard():

    cursor.execute("SELECT SUM(amount) FROM expenses")
    result = cursor.fetchone()[0]

    total_expense = result if result else 0

    cursor.execute("SELECT total_budget FROM budget LIMIT 1")
    budget = cursor.fetchone()[0]

    balance = budget - total_expense

    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    transactions = cursor.fetchall()

    return render_template(
        "dashboard.html",
        balance=balance,
        budget=budget,
        transactions=transactions
    )


@app.route('/add', methods=['GET','POST'])
def add_expense():

    if request.method == 'POST':

        category = request.form['category']
        amount = request.form['amount']
        description = request.form['description']
        date = request.form['date']

        query = "INSERT INTO expenses(category,amount,description,date) VALUES(%s,%s,%s,%s)"
        cursor.execute(query,(category,amount,description,date))
        db.commit()

        return redirect('/')

    return render_template("add_expense.html")


if __name__ == "__main__":
    app.run(debug=True)