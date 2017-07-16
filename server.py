from flask import Flask, render_template, flash, request, redirect, session
from mysqlconnection import MySQLConnector
import re
import md5

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)

mysql = MySQLConnector(app, 'login_reg_flask')

app.secret_key = "Logs"

salt = "ReallyInsecure"

@app.route('/')
def logreg():
	return render_template('log_reg.html')

@app.route('/users', methods=["POST"])
def register():
	errors = False
	if len(request.form['first_name']) < 2:
		flash('First name must be at least two characters')
		errors = True
	if not request.form['first_name'].isalpha():
		flash('First name must be all letters')
		errors = True
	if len(request.form['last_name']) < 2:
		flash('Last name must be at least two characters')
		errors = True
	if not request.form['last_name'].isalpha():
		flash('Last name must be all letters')
		errors = True
	if not re.match(EMAIL_REGEX, request.form['email']):
		flash('Email is of incorrect format.')
		errors = True
	if len(request.form['password'])<8:
		flash('Password must be at least 8 characters')
		errors = True
	if request.form['password'] != request.form['password_conf']:
		flash('Password fields must match')
		errors = True
	if errors:
		return redirect('/')
	else:
		hashed_pw = md5.new(salt+request.form['password']+salt).hexdigest()
		query = "INSERT INTO users (first_name, last_name, email, hashed_password, created_at, updated_at) VALUES (:f_n, :l_n, :em, :pw, NOW(), NOW())"
		data = {
		"f_n": request.form["first_name"],
		"l_n": request.form["last_name"],
		"em": request.form["email"],
		"pw": hashed_pw
		}
		mysql.query_db(query, data)
		return redirect('/')

@app.route('/login', methods=["POST"])
def login():
	login_query = "SELECT id, email, first_name, last_name, hashed_password FROM users WHERE email = :user_email"
	data = {"user_email": request.form['email']}
	found_user = mysql.query_db(login_query, data)
	print found_user
	hashed_input = md5.new(salt+request.form['password']+salt).hexdigest()
	if hashed_input == found_user[0]['hashed_password']:
		print "we did it"
		session['user_id'] = found_user[0]['id']
		session['user_name'] = found_user[0]['first_name'] + " " + found_user[0]['last_name']
		return redirect('/success')
	else:
		flash("you messed up")
		return redirect('/')

@app.route('/success')
def success():
	return render_template('success.html')

app.run(debug=True)


# Validations and Fields to Include
# 1. First Name - letters only, at least 2 characters and that it was submitted

# 2. Last Name - letters only, at least 2 characters and that it was submitted

# 3. Email - Valid Email format, and that it was submitted

# 4. Password - at least 8 characters, and that it was submitted

# 5. Password Confirmation - matches password