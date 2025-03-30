import os
import pickle
import sqlite3

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session

app = Flask(__name__)  # Initialize the flask App
app.secret_key = 'your_secret_key'  # Needed for session and flash messages

# Load the trained model
with open('road.pkl', 'rb') as model_file:
    road = pickle.load(model_file)
#road = pickle.load(open('road.pkl', 'rb'))

# Database file path
DATABASE = 'users.db'


# Initialize database if it doesn't exist
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/chart')
def chart():
    return render_template('chart.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        try:
            # Add user to database
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            flash('User ' + username + ' is registered successfully! User can login to the system now.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['uname']
        password = request.form['pwd']

        # Validate credentials
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            # Set session variables
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'success': True, 'redirect_url': url_for('upload')})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    return render_template('login.html')


@app.route('/upload')
def upload():
    if not session.get('logged_in'):
        flash('You must log in to access this page.', 'danger')
        return redirect(url_for('login'))
    return render_template('upload.html')

DEFAULT_FILE_PATH = "upload.csv"

@app.route('/preview', methods=["POST"])
def preview():
    print(request.files, request.files['datasetfile'])
    if 'datasetfile' in request.files and request.files['datasetfile'].filename != '':
        #         # Case 1: User uploaded a file via <input type="file">
        dataset = request.files['datasetfile']
        print("User uploaded file: {}".format(dataset.filename))
    else:
        # Case 2: User clicked "Use Default File"
        dataset = DEFAULT_FILE_PATH
        print("Using default file: {}".format(DEFAULT_FILE_PATH))

    # Read the dataset (either uploaded or default)
    df = pd.read_csv(dataset, encoding='unicode_escape')
    df.set_index('Id', inplace=True)

    return render_template("preview.html", df_view=df)


@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    return render_template('prediction.html')


@app.route('/predict', methods=['POST'])
def predict():
    int_feature = [x for x in request.form.values()]
    final_features = [np.array(int_feature)]
    result = road.predict(final_features)
    for i in result:
        print(i, end="")
        if i == 1:
            prediction_text = "Slight: Slight Injury may occur, So Drive Carefully"
        elif i == 2:
            prediction_text = "Serious: Serious Injury may occur, So Drive Very Carefully"
        elif i == 3:
            prediction_text = "Fatal: Death may occur, So Drive Very Very Carefully"
    return render_template('prediction.html', prediction_text=prediction_text)

@app.route('/performance')
def performance():
    return render_template('performance.html')


if __name__ == "__main__":
    init_db()  # Ensure the database is initialized
    app.run(debug=True)
