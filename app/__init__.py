from flask import Flask, render_template, request, redirect, url_for, session, flash

import data

app = Flask(__name__)
app.secret_key = "vsecretandsecurekeyforstuyoverflow"
data.create_tables()

#login
@app.route("/", methods=["GET", "POST"])
def login():
    if 'email' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        if data.auth(email, password):
            return redirect(url_for('index'))
        else:
            flash("Email or password incorrect. Try again.")
            return redirect(url_for('login'))
    return render_template('login.html')


#register
@app.route("/register", methods = ['GET', "POST"])
def set_user():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if data.user_exists(email):
            flash("User already exists!")
            return redirect(url_for('set_user'))
        github = request.form['github']
        name = request.form['name']
        data.add_user(email, password, name, github)
        session['email'] = email
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

#main
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

# TEST
@app.route("/post_test")
def posts():
    return render_template("post_test.html")

#handling data
#@app.route('/data')

if __name__ == "__main__":
  app.debug = True
  app.run()
