from flask import Flask, render_template, request, redirect, url_for, session

import data

app = Flask(__name__)
app.secret_key = "vsecretandsecurekeyforstuyoverflow"

#login
@app.route("/", methods=["GET", "POST"])
def login():
    if 'email' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        userData = data.auth(email, password)
        if userData:
            if password == userData["password"]:
                session["email"] = email
                return redirect(url_for('index'))
            else:
                flash("Incorrect password. Try again.")
        else:
            flash("Email incorrect or not found. Try again.")
        return redirect(url_for('login'))
    return render_template('login.html')


#createaccount
@app.route("/createaccount", methods = ['GET', "POST"])
def set_user():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if user_exists(email):
            flash("User exists!")
            return redirect(url_for('set_user'))
        github = request.form['github']
        name = request.form['name']
        is_dojo = request.form['is_dojo']
        classes = request.form['classes']
        add_user(password, email, github, name, is_dojo, classes)
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('createaccount.html')

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

#main
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

#handling data
#@app.route('/data')

if __name__ == "__main__":
  app.debug = True
  app.run()
