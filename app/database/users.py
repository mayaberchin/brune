import hashlib                      # for consistent hashes
from datetime import datetime       # for dates/times

import tables, helpers, classes, posts

#---------[accessors]---------#


# returns a list of emails
def get_all_users():
    data = tables.get_col("users", "email")
    return data

def get_all_dojo():
    return [user for user in get_all_users() if is_dojo(user)]

def get_all_senseis():
    return [user for user in get_all_users() if is_sensei(user)]

def get_all_teachers():
    return [user for user in get_all_users() if is_stuy_teacher(user)]



def get_user_name(email):
    if not email:
        return "Anonymous"
    return get_users_field(email, 'name')

def get_user_passhash(email):
    return get_users_field(email, 'password_hash')

def get_user_github(email):
    return get_users_field(email, 'github')


def get_pinged_posts(email):
    pinged_posts_str = get_users_field(email, 'pinged_posts')
    pinged_posts = helpers.make_list(pinged_posts_str)
    pinged_posts = posts.sort_by_ctime(pinged_posts)
    return pinged_posts

# returns unread posts from announcements, questions, and notes (but not groupchat) from any class
def get_top_n_pinged(email, n):
    all = get_pinged_posts(email)
    # prioritize announcements, then questions, then notes (don't get gc)
    announcements = []
    questions = []
    notes = []
    for post in all:
        type = posts.get_post_category(post)
        if type == 'announcement':
            announcements += [post]
        elif type == 'question':
            questions += [post]
        elif type == 'notes':
            notes += [post]
    ordered = announcements[:n]
    ordered += questions[:n-len(ordered)]
    ordered += notes[:n-len(ordered)]
    return ordered


def get_unread_posts(email):
    unread_posts_str = get_users_field(email, 'unread_posts')
    unread_posts = helpers.make_list(unread_posts_str)
    unread_posts = helpers.sort_by_ctime(unread_posts)
    return unread_posts

# returns unread posts from announcements, questions, and notes (but not groupchat) from any class
def get_top_n_unread(email, n):
    all = get_unread_posts(email)
    # prioritize announcements, then questions, then notes (don't get gc)
    announcements = []
    questions = []
    notes = []
    for post in all:
        type = posts.get_post_category(post)
        if type == 'announcement':
            announcements += [post]
        elif type == 'question':
            questions += [post]
        elif type == 'notes':
            notes += [post]
    ordered = announcements[:n]
    ordered += questions[:n-len(ordered)]
    ordered += notes[:n-len(ordered)]
    return ordered


# returns at most one message (if there is an unread one) from the groupchat of at most n classes
def get_top_n_gc(email, n):
    all = get_unread_posts(email)
    gc = [post for post in all if posts.get_post_category(post) == 'groupchat']
    messages = []
    classes = []
    while len(gc) > 0 and len(classes) < n:
        msg_class = posts.get_post_class(gc[-1])
        if msg_class not in classes:
            classes += msg_class
            messages += [{gc[-1]: msg_class}]
            gc.remove(gc[-1])
    messages = posts.sort_by_ctime(messages)
    return messages


# returns a dictionary of stuff to display on the homepage
def get_homepage_posts(email, n):
    # get a list of pinged posts
    pinged = get_top_n_pinged(email, n)
    # get a list of unread posts if there aren't enough pinged posts
    unread = []
    if len(pinged) < n:
        unread = get_top_n_unread(email, n-len(pinged))
    posts = {}
    posts['pinged'] = posts.sort_by_ctime(pinged)
    posts['unread'] = posts.sort_by_ctime(unread)
    return posts



# get the classes someone is in
def get_user_classes(email):
    user_classes = []
    classes = classes.get_all_classes()
    for c in classes:
        members = classes.get_class_members(c)
        if email in members:
            user_classes.append(c)
    return user_classes

# get the classes someone teaches
def get_teaching_classes(email):
    classes = get_user_classes(email)
    teaches = [c for c in classes if email in classes.get_class_teachers(c)]
    return teaches

# get the classes someone owns
def get_owned_classes(email):
    classes = get_user_classes(email)
    owned = [c for c in classes if email in classes.get_class_owners(c)]
    return owned


def get_user_data(email):
    keys = tables.USERS_COLS
    values = tables.get_row('users', 'email', email)
    d = helpers.list_to_dict(keys, values)
    d['class_id'] = helpers.make_list(d['class_id'])
    d['unread_posts'] = helpers.make_list(d['unread_posts'])
    d['pinged_posts'] = helpers.make_list(d['pinged_posts'])
    return d



def is_dojo(email):
    dojo = get_users_field(email, 'is_dojo')
    return dojo == 'yes'

def is_sensei(email):
    sensei = get_users_field(email, 'is_sensei')
    return sensei == 'yes'

def is_stuy_teacher(email):
    teacher = get_users_field(email, 'is_stuy_teacher')
    return teacher == 'yes'




#---------[modifiers]---------#

# adds a new user's data to user table
def add_user(email, password, name, github=''):
    if user_exists(email):
        return 'There is already a user with this email'
    if password == "":
        return 'Password cannot be empty'
    password = password.encode('utf-8')
    password = str(hashlib.sha256(password).hexdigest())
    is_dojo = 'no'
    is_sensei = 'no'
    is_stuy_teacher = 'no'
    class_id = ''
    unread_posts = ''
    pinged_posts = ''
    add_users_row([email, github, name, password, is_dojo, is_sensei, is_stuy_teacher, class_id, unread_posts, pinged_posts])
    return 'success'


def add_dojo(email):
    update_users_row(email, 'is_dojo', 'yes')

def add_sensei(email):
    update_users_row(email, 'is_dojo', 'yes')
    update_users_row(email, 'is_sensei', 'yes')

def add_teacher(email):
    update_users_row(email, 'is_stuy_teacher', 'yes')

def mark_read(email, post_id):
    pinged_posts = get_pinged_posts(email)
    unread_posts = get_unread_posts(email)
    if (post_id in pinged_posts):
        pinged_posts.remove(post_id)
        pinged_str = merge_list(pinged_posts)
        update_users_row(email, 'pinged_posts', pinged_str)
    if (post_id in unread_posts):
        unread_posts.remove(post_id)
        unread_str = merge_list(unread_posts)
        update_users_row(email, 'unread_posts', unread_str)



#---------[verification]---------#


# returns whether or not a user exists
def user_exists(email):
    all_users = get_all_users()
    for user in all_users:
        if (user == email):
            return True
    return False

# checks if provided password in login attempt matches user password
def auth(email, password):
    if not user_exists(email):
        return False
    real_pass = get_user_passhash(email)
    password = password.encode('utf-8')
    if real_pass != str(hashlib.sha256(password).hexdigest()):
        return False
    return True



#---------[users-helpers]---------#


def get_users_field(email, field_name):
    return helpers.get_field('users', 'email', email, field_name)

def add_users_row(values):
    tables.add_row('users', values)

def update_users_row(email, col_name, col_val):
    tables.update_row('users', 'email', email, col_name, col_val)

def delete_users_row(ID_fieldname, id):
    tables.delete_row('users', ID_fieldname, id)