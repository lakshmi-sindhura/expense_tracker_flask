from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'secret123'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sql@123'
app.config['MYSQL_DB'] = 'expense_tracker'

mysql = MySQL(app)


def create_table():
    cursor = mysql.connection.cursor()

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount DECIMAL(10,2),
            category VARCHAR(50),
            description TEXT,
            date DATE,
            user_id INT
        )
    """)

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            password VARCHAR(100)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
           id INT AUTO_INCREMENT PRIMARY KEY,
           title VARCHAR(100),
           reminder_date DATE,
           user_id INT
        )
    """)

    mysql.connection.commit()
    cursor.close()



@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    create_table()

    user_id = session['user_id']
    filter_type = request.args.get('filter')
    cursor = mysql.connection.cursor()
    cursor.execute("""
    SELECT * FROM reminders 
    WHERE user_id=%s 
    ORDER BY reminder_date ASC
""", (user_id,))
    reminders = cursor.fetchall()

    cursor = mysql.connection.cursor()

    if filter_type == 'today':
        cursor.execute(
            "SELECT * FROM expenses WHERE user_id=%s AND date = CURDATE()",
            (user_id,)
        )
        expenses = cursor.fetchall()

        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id=%s AND date = CURDATE()",
            (user_id,)
        )
        total = cursor.fetchone()[0]

    elif filter_type == 'month':
        cursor.execute("""
            SELECT * FROM expenses 
            WHERE user_id=%s AND MONTH(date)=MONTH(CURDATE()) 
            AND YEAR(date)=YEAR(CURDATE())
        """, (user_id,))
        expenses = cursor.fetchall()

        cursor.execute("""
            SELECT SUM(amount) FROM expenses 
            WHERE user_id=%s AND MONTH(date)=MONTH(CURDATE()) 
            AND YEAR(date)=YEAR(CURDATE())
        """, (user_id,))
        total = cursor.fetchone()[0]

    else:
        cursor.execute(
            "SELECT * FROM expenses WHERE user_id=%s",
            (user_id,)
        )
        expenses = cursor.fetchall()

        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id=%s",
            (user_id,)
        )
        total = cursor.fetchone()[0]

   
    cursor.execute("""
        SELECT MONTH(date), YEAR(date), SUM(amount)
        FROM expenses
        WHERE user_id=%s
        GROUP BY YEAR(date), MONTH(date)
        ORDER BY YEAR(date) DESC, MONTH(date) DESC
    """, (user_id,))
    monthly_data = cursor.fetchall()

    cursor.close()

    return render_template(
    'index.html',
    expenses=expenses,
    total=total,
    monthly_data=monthly_data,
    reminders=reminders
)


@app.route('/add', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect('/login')

    try:
        create_table()

        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO expenses (amount, category, description, date, user_id) VALUES (%s, %s, %s, %s, %s)",
            (amount, category, description, date, user_id)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect('/')

    except Exception as e:
        return str(e)



@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor = mysql.connection.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE id=%s AND user_id=%s",
        (id, user_id)
    )
    mysql.connection.commit()
    cursor.close()

    return redirect('/')



@app.route('/edit/<int:id>')
def edit(id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM expenses WHERE id=%s AND user_id=%s",
        (id, user_id)
    )
    expense = cursor.fetchone()
    cursor.close()

    return render_template('edit.html', expense=expense)



@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if 'user_id' not in session:
        return redirect('/login')

    try:
        user_id = session['user_id']

        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE expenses 
            SET amount=%s, category=%s, description=%s, date=%s
            WHERE id=%s AND user_id=%s
        """, (amount, category, description, date, id, user_id))

        mysql.connection.commit()
        cursor.close()

        return redirect('/')

    except Exception as e:
        return str(e)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect('/login')

    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')
@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    if 'user_id' not in session:
        return redirect('/login')

    title = request.form['title']
    date = request.form['date']
    user_id = session['user_id']

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO reminders (title, reminder_date, user_id) VALUES (%s, %s, %s)",
        (title, date, user_id)
    )
    mysql.connection.commit()
    cursor.close()

    return redirect('/')



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)


