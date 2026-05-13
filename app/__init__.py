from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

#login
@app.route("/", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        userData = mongo.users.find_one({"_id": username}, {"password":1})
        if userData:
            if password == userData["password"]:
                session["username"] = username
                return redirect(url_for('index'))
            else:
                flash("Incorrect password. Try again.")
        else:
            flash("Username incorrect or not found. Try again.")
        return redirect(url_for('login'))
    return render_template('login.html')


#createaccount
@app.route("/createaccount", methods = ['GET', "POST"])
def set_user():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if mongo.users.find_one({"_id": username}):
            flash("Username already taken!")
            return redirect(url_for('set_user'))
        mongo.users.insert_one({
            "_id": username,
            "password": password
        })
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('createaccount.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#main
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

#handling data
@app.route('/data')

if __name__ == "__main__":
  app.debug = True
  app.run()
