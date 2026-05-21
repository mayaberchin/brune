from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

import data

app = Flask(__name__)
app.secret_key = "vsecretandsecurekeyforstuyoverflow"
data.create_tables()

TEST_CLASSES = [
    {"class_id": 1, "name": "Software Development"},
    {"class_id": 2, "name": "Systems"},
    {"class_id": 3, "name": "Cybersecurity"},
]

POST_PAGE_INFO = {
    "announcements": {
        "page_title": "Announcements",
        "page_description": "Teacher posts, assignments, and important class updates.",
        "selected_post_type": "announcement",
        "new_post_label": "New Announcement",
    },
    "questions": {
        "page_title": "Questions",
        "page_description": "Ask longer questions and provide context for help.",
        "selected_post_type": "question",
        "new_post_label": "New Question",
    },
    "chat": {
        "page_title": "Chat",
        "page_description": "CHat!!!!",
        "selected_post_type": "chat",
        "new_post_label": "New Chat",
    },
    "notes_resources": {
        "page_title": "Notes / Resources",
        "page_description": "Share notes, reminders, links, and useful resources.",
        "selected_post_type": "note",
        "new_post_label": "New Note",
    },
}

#login
@app.route("/", methods=["GET", "POST"])
def login():
    if 'email' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        if data.auth(email, password):
            session['email'] = email
            return redirect(url_for('home'))
        else:
            flash("Email or password incorrect. Try again.")
            return redirect(url_for('login'))
    return render_template('login.html')


#register
@app.route("/register", methods = ['GET', "POST"])
def set_user():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if data.user_exists(email):
            flash("User already exists!")
            return redirect(url_for('set_user'))
        github = request.form.get('github')
        name = request.form.get('name')
        data.add_user(email, password, name, github)
        session['email'] = email;
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

#main
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template("homepage.html")



# ------------------ POST PAGES ------------------

def render_post_page(page):
    page_info = POST_PAGE_INFO[page]
    return render_template(
        "post_page.html",
        classes=TEST_CLASSES,
        page_title=page_info["page_title"],
        page_description=page_info["page_description"],
        selected_post_type=page_info["selected_post_type"],
        new_post_label=page_info["new_post_label"]
    )

@app.route("/announcements")
def announcements():
    return render_post_page("announcements")


@app.route("/questions")
def questions():
    return render_post_page("questions")


@app.route("/chat")
def chat():
    return render_post_page("chat")


@app.route("/notes_resources")
def notes_rsrc():
    return render_post_page("notes_resources")



# ------------------ REACT POST API ROUTES ------------------

# loads posts
@app.route("/api/posts")
def api_posts():
    category = request.args.get("category", "")
    posts = []

    for post_id in data.get_all_posts(): # list of all post IDs in db
        post = data.get_post_data(post_id)

        if category == "" or post["category"] == category:
            posts.append(post)

    posts.reverse() # newest posts first
    return jsonify({"posts": posts})

# ceates and saves a new post
@app.route("/api/posts", methods=["POST"])
def api_create_post():
    post = request.get_json()

    title = post.get("title", "").strip()
    class_id = post.get("class_id", "").strip()
    body = post.get("body", "").strip()
    category = post.get("category", "").strip()

    post_id = data.create_post( # returns new post_id
        session["email"],
        class_id,
        title,
        body,
        category
    )
    saved_post = data.get_post_data(post_id)
    return jsonify({"post": saved_post})

#handling data
#@app.route('/data')

if __name__ == "__main__":
  app.debug = True
  app.run()
