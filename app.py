from flask import Flask, render_template,  request, redirect, url_for, session
from joblib import load
import mysql.connector
import re
# App definition
app = Flask(__name__)

app.secret_key = 'key'

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'sagar bhavsar',
    'password': 'VVsagar@1',
    'database': 'db',
}

# Function to establish a MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(**db_config)

# Load trained classifier
with open('models/LR_model.pkl', 'rb') as file:
    model = load(file)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/result', methods=['POST'])
def get_result():
    if request.method == 'POST':
        input_text = request.form['text']
        data = [input_text]
        result = model.predict(data)
        if int(result) == 1:
            my_prediction = "This review is positive"
        else:
            my_prediction = "This review is negative"
        return render_template("result.html", prediction=my_prediction)
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM credentials WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            return render_template('result.html', msg=msg)
        else:
            msg = 'Incorrect username / password!'
        cursor.close()
        connection.close()
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM credentials WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO credentials VALUES (NULL, %s, %s, %s)', (username, password, email))
            connection.commit()
            msg = 'You have successfully registered!'
        cursor.close()
        connection.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)
if __name__ == '__main__':
    app.run(debug=True)
