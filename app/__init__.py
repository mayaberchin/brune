from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

import data

app = Flask(__name__)
app.secret_key = "vsecretandsecurekeyforstuyoverflow"
data.create_tables()

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

    # get homepage posts
    homepage_post_ids = data.get_homepage_posts(session['email'],20)
    homepage_posts = []
    for post_id in homepage_post_ids['pinged'] + homepage_post_ids['unread']:
        post_data = data.get_post_data(post_id)
        homepage_posts.append(post_data)
    homepage_posts.reverse()

    # get updated posts ============================need to do
    updated_posts = []

    # get unresolved posts
    unresolved_post_ids = data.get_all_unresolved()
    unresolved_posts = []
    for post_id in unresolved_post_ids:
        post_data = data.get_post_data(post_id)
        unresolved_posts.append(post_data)
    unresolved_posts.reverse()


    # get instructors posts ===========================need to do
    instructors_posts = []



    # get courses
    class_ids = data.get_user_classes(session['email'])
    classes = []
    for class_id in class_ids:
        classes.append({
            "class_id": class_id,
            "name": data.get_class_name(class_id),
        })

    unread_posts = []
    for post_id in data.get_unread_posts(session['email']):
        unread_posts.append(data.get_post_data(post_id))

    return render_template(
        "homepage.html",
        homepage_posts=homepage_posts,
        updated_posts=updated_posts,
        unresolved_posts=unresolved_posts,
        instructors_posts=instructors_posts,
        unread_posts=unread_posts,
        classes=classes,
        get_user_name=data.get_user_name
    )





# ------------------ POST PAGES ------------------

def render_post_page(page):
    if 'email' not in session:
        return redirect(url_for('login'))

    page_info = POST_PAGE_INFO[page]
    can_post = page != "announcements" or data.is_stuy_teacher(session["email"])
    return render_template(
        "post_page.html",
        page_title=page_info["page_title"],
        page_description=page_info["page_description"],
        selected_post_type=page_info["selected_post_type"],
        new_post_label=page_info["new_post_label"],
        can_post=can_post,
        current_user_email=session["email"]
    )

@app.route("/announcements")
def announcements():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_post_page("announcements")



@app.route("/pinned")
def pinned():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template("pinned.html")
    #return render_post_page("pinned")


@app.route("/questions")
def questions():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_post_page("questions")


@app.route("/chat")
def chat():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_post_page("chat")


@app.route("/notes_resources")
def notes_rsrc():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_post_page("notes_resources")


@app.route("/account")
def account():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template("account.html")

@app.route("/settings")
def settings():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template("settings.html")

# ------------------ REACT POST API ROUTES ------------------

@app.route("/api/classes")
def api_classes():
    classes = []

    for class_id in data.get_user_classes(session["email"]):
        classes.append({
            "class_id": class_id,
            "name": data.get_class_name(class_id),
            "is_teacher": data.is_class_teacher(class_id, session["email"]),
        })

    return jsonify({"classes": classes})

# loads posts
@app.route("/api/posts")
def api_posts():
    category = request.args.get("category", "")
    posts = []

    for post_id in data.get_all_posts(): # list of all post IDs in db
        post = data.get_post_data(post_id)
        post = add_display_author(post)

        if post["parent_id"] == "" and (category == "" or post["category"] == category):
            posts.append(post)

    posts.reverse() # newest posts first
    return jsonify({"posts": posts})

# ceates and saves a new post
@app.route("/api/posts", methods=["POST"])
def api_create_post():
    post = request.get_json() or {}

    title = post.get("title", "").strip()
    class_id = post.get("class_id", "").strip()
    body = post.get("body", "").strip()
    category = post.get("category", "").strip()
    show_dojo = "yes" if post.get("shareWithDojo") else "no"
    is_anonymous = "yes" if post.get("isAnonymous") else "no"

    if category == "announcement" and not data.is_class_teacher(class_id, session["email"]):
        return jsonify({"error": "Only teachers can post announcements"}), 403

    post_id = data.create_post( # returns new post_id
        session["email"],
        class_id,
        title,
        body,
        category,
        show_dojo,
        "", # attachments
        is_anonymous
    )
    saved_post = data.get_post_data(post_id)
    saved_post = add_display_author(saved_post)
    return jsonify({"post": saved_post})

@app.route("/api/posts/<post_id>/followups")
def api_followups(post_id):
    followup_ids = data.get_post_followups(post_id)
    if type(followup_ids) == list:
        followup_ids = {
            "answers": [],
            "teacher_responses": [],
            "other": followup_ids,
        }
    followups = {
        "answers": [],
        "teacher_responses": [],
        "other": [],
    }

    for group in followups:
        for followup_id in followup_ids[group]:
            followup = data.get_post_data(followup_id)
            followup = add_display_author(followup)
            followups[group].append(followup)

    return jsonify({"followups": followups})

@app.route("/api/posts/<post_id>/followups", methods=["POST"])
def api_create_followup(post_id):
    post = request.get_json() or {}
    body = post.get("body", "").strip()
    is_anonymous = "yes" if post.get("isAnonymous") else "no"

    if body == "":
        return jsonify({"error": "Missing followup body"}), 400

    followup_id = data.create_followup(session["email"], post_id, body, is_anonymous)
    followup = data.get_post_data(followup_id)
    followup = add_display_author(followup)
    return jsonify({"followup": followup})

@app.route("/api/posts/<post_id>/upvote", methods=["POST"])
def api_toggle_upvote(post_id):
    try:
        post = data.get_post_data(post_id)
    except IndexError:
        return jsonify({"error": "Post not found"}), 404

    if session["email"] in post["upvoters"]:
        data.remove_post_upvoter(post_id, session["email"])
    else:
        data.add_post_upvoter(post_id, session["email"])

    post = data.get_post_data(post_id)
    post = add_display_author(post)
    return jsonify({"post": post})

@app.route("/api/posts/<post_id>", methods=["DELETE"])
def api_delete_post(post_id):
    try:
        post = data.get_post_data(post_id)
    except IndexError:
        return jsonify({"error": "Post not found"}), 404

    if not data.is_class_teacher(post["class_id"], session["email"]):
        return jsonify({"error": "Only teachers of this class can delete posts"}), 403

    data.delete_post(post_id)
    return jsonify({"deleted": post_id})

def add_display_author(post):
    if post["is_anonymous"] == "yes":
        post["display_author"] = "Anonymous"
    else:
        post["display_author"] = data.get_user_name(post["author_email"])
    post["has_upvoted"] = 'email' in session and session["email"] in post["upvoters"]
    post["can_delete"] = (
        post["category"] != "chat"
        and 'email' in session
        and data.is_class_teacher(post["class_id"], session["email"])
    )
    return post

#join/create class:
@app.route("/join_class", methods=["POST"])
def join_a_class():
    print("joining")
    code = request.form.get("class_code", "").strip()
    print(data.get_all_classes())
    if code not in data.get_all_classes():
        print(data.get_all_classes())
        flash("Class not found. Ask your teacher for the code.")
        return redirect(url_for("home"))
    data.add_class_member(code, session['email'])
    return redirect(url_for("home"))

@app.route("/create_class_",methods=["POST"])
def create_a_class():
    print("creating")
    class_name = request.form.get("class_name", "").strip()
    if class_name == "":
        flash("Class name cannot be empty.")
        return redirect(url_for("home"))
    class_id = data.create_class(session['email'], class_name)
    flash("Class created! Code: " + class_id)
    print("Class created")
    return redirect(url_for("home"))


if __name__ == "__main__":
  app.debug = True
  app.run()
