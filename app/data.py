import sqlite3                      # enable control of a sqlite database
import hashlib                      # for consistent hashes
import secrets                      # to generate ids
from datetime import datetime       # for dates/times


DB_FILE="data.db"


#=============================[GLOBALS]=============================#

USERS_COLS = ['email', 'github', 'name', 'password_hash', 'is_dojo', 'is_sensei', 'is_stuy_teacher', 'class_id', 'unread_posts', 'pinged_posts']
CLASSES_COLS = ['class_id', 'name', 'owner_email', 'teacher_email', 'member_email', 'banned_email', 'posts', 'is_archived']
POSTS_COLS = ['post_id', 'author_email', 'class_id', 'parent_id', 'title', 'body', 'attachments', 'category', 'is_resolved', 'is_answer', 'created_at', 'updated_at', 'upvotes', 'upvoters', 'ping', 'show_dojo', 'is_anonymous']


#=============================[MAKE=TABLES]=============================#


# users
def create_users_table():
    command =  """
                CREATE TABLE IF NOT EXISTS users (
                    email           TEXT        NOT NULL    PRIMARY KEY     UNIQUE,
                    github          TEXT,
                    name            TEXT        NOT NULL,
                    password_hash   TEXT        NOT NULL,
                    is_dojo         TEXT        NOT NULL                                DEFAULT 'no',
                    is_sensei       TEXT        NOT NULL                                DEFAULT 'no',
                    is_stuy_teacher TEXT        NOT NULL                                DEFAULT 'no',
                    class_id        TEXT,
                    unread_posts    TEXT,
                    pinged_posts    TEXT
                )"""
    sqlite(command)

# classes
def create_classes_table():
    command =  """
                CREATE TABLE IF NOT EXISTS classes (
                    class_id        TEXT        NOT NULL    PRIMARY KEY,
                    name            TEXT        NOT NULL,
                    owner_email     TEXT        NOT NULL,
                    teacher_email   TEXT        NOT NULL,
                    member_email    TEXT        NOT NULL,
                    banned_email    TEXT,
                    posts           TEXT,
                    is_archived     TEXT        NOT NULL
                )"""
    sqlite(command)

# posts
def create_posts_table():
    command =  """
                CREATE TABLE IF NOT EXISTS posts (
                    post_id         TEXT        NOT NULL    PRIMARY KEY,
                    author_email    TEXT        NOT NULL,
                    class_id        TEXT        NOT NULL,
                    parent_id       TEXT,
                    title           TEXT,
                    body            TEXT        NOT NULL,
                    attachments     TEXT,
                    category        TEXT        NOT NULL,
                    is_resolved     TEXT,
                    is_answer       TEXT,
                    created_at      TEXT        NOT NULL                                DEFAULT CURRENT_TIMESTAMP,
                    updated_at      TEXT        NOT NULL                                DEFAULT CURRENT_TIMESTAMP,
                    upvotes         INTEGER     NOT NULL,
                    upvoters        TEXT,
                    ping            TEXT,
                    show_dojo       TEXT        NOT NULL,
                    is_anonymous    TEXT        NOT NULL
                )"""
    sqlite(command)
    # add attachement in


# all
def create_tables():
    create_users_table()
    create_classes_table()
    create_posts_table()



#=============================[USERS]=============================#



#---------[accessors]---------#


# returns a list of emails
def get_all_users():
    data = get_col("users", "email")
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

def get_user_password(email):
    return get_users_field(email, 'password_hash')

def get_user_github(email):
    get_users_field(email, 'github')


def get_pinged_posts(email):
    pinged_posts_str = get_users_field(email, 'pinged_posts')
    pinged_posts = make_list(pinged_posts_str)
    pinged_posts = sort_by_ctime(pinged_posts)
    return pinged_posts

# returns unread posts from announcements, questions, and notes (but not groupchat) from any class
def get_top_n_pinged(email, n):
    all = get_pinged_posts(email)
    # prioritize announcements, then questions, then notes (don't get gc)
    announcements = []
    questions = []
    notes = []
    for post in all:
        type = get_post_category(post)
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
    unread_posts = make_list(unread_posts_str)
    unread_posts = sort_by_ctime(unread_posts)
    return unread_posts

# returns unread posts from announcements, questions, and notes (but not groupchat) from any class
def get_top_n_unread(email, n):
    all = get_unread_posts(email)
    # prioritize announcements, then questions, then notes (don't get gc)
    announcements = []
    questions = []
    notes = []
    for post in all:
        type = get_post_category(post)
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
    gc = [post for post in all if get_post_category(post) == 'groupchat']
    messages = []
    classes = []
    while len(gc) > 0 and len(classes) < n:
        msg_class = get_post_class(gc[-1])
        if msg_class not in classes:
            classes += msg_class
            messages += [{gc[-1]: msg_class}]
            gc.remove(gc[-1])
    messages = sort_by_ctime(messages)
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
    posts['pinged'] = sort_by_ctime(pinged)
    posts['unread'] = sort_by_ctime(unread)
    return posts



# get the classes someone is in
def get_user_classes(email):
    # print('here in get_user_classes')
    # classes_str = get_users_field(email, 'class_id')
    # print("finding all the classes for a user")
    # print(classes_str) #prints none
    # classes = make_list(classes_str)

    user_classes = []
    classes = get_all_classes()
    for c in classes:
        members = get_class_members(c)
        if email in members:
            user_classes.append(c)
    return user_classes

# get the classes someone teaches
def get_teaching_classes(email):
    classes = get_user_classes(email)
    teaches = [c for c in classes if email in get_class_teachers(c)]
    return teaches

# get the classes someone owns
def get_owned_classes(email):
    classes = get_user_classes(email)
    owned = [c for c in classes if email in get_class_owners(c)]
    return owned


def get_user_data(email):
    keys = USERS_COLS
    values = get_row('users', 'email', email)
    d = list_to_dict(keys, values)
    d['class_id'] = make_list(d['class_id'])
    d['unread_posts'] = make_list(d['unread_posts'])
    d['pinged_posts'] = make_list(d['pinged_posts'])
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
    real_pass = get_user_password(email)
    password = password.encode('utf-8')
    if real_pass != str(hashlib.sha256(password).hexdigest()):
        return False
    return True



#---------[users-helpers]---------#


def get_users_field(email, field_name):
    return get_field('users', 'email', email, field_name)

def add_users_row(values):
    add_row('users', values)

def update_users_row(email, col_name, col_val):
    update_row('users', 'email', email, col_name, col_val)




#=============================[CLASSES]=============================#


#---------[accessors]---------#


def get_active_classes():
    classes = get_all_classes()
    return [c for c in classes if not is_archived(c)]

def get_all_classes():
    data = get_col('classes', 'class_id')
    return data



def get_class_name(class_id):
    return get_classes_field(class_id, 'name')



def get_class_members(class_id):
    members_str = get_classes_field(class_id, 'member_email')
    members = make_list(members_str)
    return members

# get the teachers of a class
def get_class_teachers(class_id):
    teachers_str = get_classes_field(class_id, 'teacher_email')
    teachers = make_list(teachers_str)
    return teachers

def get_class_owners(class_id):
    owners_str = get_classes_field(class_id, 'owner_email')
    owners = make_list(owners_str)
    return owners

def get_banned_members(class_id):
    banned_str = get_classes_field(class_id, 'banned_email')
    banned = make_list(banned_str)
    return banned



def get_class_posts(class_id):
    data = get_classes_field(class_id, 'posts')
    posts = make_list(data)
    posts = sort_by_ctime(posts)
    return posts

# return only top-level posts, not followups
def get_head_posts(class_id):
    posts = [post for post in get_class_posts(class_id) if get_post_depth(post) == 0]
    posts = sort_by_ctime(posts)
    return posts

def get_teacher_posts(class_id):
    posts = get_class_posts(class_id)
    teachers = get_class_teachers(class_id)
    t_posts = []
    for post in posts:
        if get_post_author(post) in teachers:
            t_posts += [post]
    return t_posts

def get_teacher_head_posts(class_id):
    posts = get_head_posts(class_id)
    teachers = get_class_teachers(class_id)
    t_posts = []
    for post in posts:
        if get_post_author(post) in teachers:
            t_posts += [post]
    return t_posts

def get_class_announcements(class_id):
    posts = [post for post in get_head_posts(class_id) if get_post_category(post) == 'announcement']
    posts = sort_by_ctime(posts)
    return posts

def get_class_questions(class_id):
    posts = [post for post in get_head_posts(class_id) if get_post_category(post) == 'question']
    posts = sort_by_ctime(posts)
    return posts

def get_class_notes(class_id):
    posts = [post for post in get_head_posts(class_id) if get_post_category(post) == 'note']
    posts = sort_by_ctime(posts)
    return posts

def get_class_n_gc(class_id, n=-1):
    posts = get_class_posts(class_id)
    posts = sort_by_ctime(posts)
    gc = [post for post in posts if get_post_category(post) == 'chat']
    if (n > 0):
        return gc[:n]
    return gc

def get_class_gc_by(class_id, email):
    posts = get_class_posts(class_id)
    posts = sort_by_ctime(posts)
    gc = [post for post in posts if get_post_category(post) == 'chat' and get_post_author(post) == email]
    return gc


def get_class_data(class_id):
    keys = CLASSES_COLS
    values = get_row('classes', 'class_id', class_id)
    d = list_to_dict(keys, values)
    d['teacher_email'] = make_list(d['teacher_email'])
    d['posts'] = make_list(d['posts'])
    d['posts'] = sort_by_ctime(d['posts'])
    return d



def is_archived(class_id):
    return get_classes_field(class_id, 'is_archived') == 'yes'

def is_class_teacher(class_id, email):
    return email in get_class_teachers(class_id)

def is_class_owner(class_id, email):
    return email in get_class_owners(class_id)

def is_banned(class_id, email):
    return email in get_banned_members(class_id)



#---------[class-creation-deletion]---------#


def create_class(teacher_email, class_name):
    print("create class called")
    # add the class to classes table
    class_id = gen_id(get_all_classes(), 3)
    owner = teacher_email
    members = teacher_email
    posts = ''
    is_archived = 'no'
    banned = ''
    add_classes_row([class_id, class_name, owner, teacher_email, members, banned, posts, is_archived])
    # add the class to teacher's users table
    teacher_classes = get_user_classes(teacher_email)
    teacher_classes_str = add_to_list(teacher_classes, class_id)
    update_users_row(teacher_email, 'class_id', teacher_classes_str)
    return class_id


def delete_class(class_id):
    members = get_class_members(class_id)
    for member in members:
        remove_member(class_id, member, True)
    delete_row('classes', 'class_id', class_id)


#---------[modifiers]---------#


def change_class_name(class_id, new_name):
    update_classes_row(class_id, 'name', new_name)



def archive_class(class_id):
    update_classes_row(class_id, 'is_archived', 'yes')

def un_archive_class(class_id):
    update_classes_row(class_id, 'is_archived', 'no')



# add a user to a class as a student
def add_class_member(class_id, email):
    banned = get_banned_members(class_id)
    if email in banned:
        return 'nuh uh, you\'re banned lil bro'
    classes = get_user_classes(email)
    classes_updated = add_to_list(classes, class_id)
    update_users_row(email, 'class_id', classes_updated)
    users = get_class_members(class_id)
    users_updated = add_to_list(users, email)
    update_classes_row(class_id, 'member_email', users_updated)
    return 'oke'



# promote a class member to a teacher for that class
def promote_to_teacher(class_id, email):
    teachers = get_class_teachers(class_id)
    teachers_str = add_to_list(teachers, email)
    update_classes_row(class_id, 'teacher_email', teachers_str)

# promote a class member to an owner for that class
def promote_to_owner(class_id, email):
    owners = get_class_owners(class_id)
    owners_str = add_to_list(owners, email)
    update_classes_row(class_id, 'owner_email', owners_str)
    # add them to teachers list if they aren't there yet
    if email not in get_class_teachers(class_id):
        promote_to_teacher(class_id, email)



def demote_teacher(class_id, email):
    teachers = get_class_teachers(class_id)
    teachers_str = remove_from_list(teachers, email)
    update_classes_row(class_id, 'teacher_email', teachers_str)

def demote_owner(class_id, email, leave_as_teacher=True):
    owners = get_class_owners(class_id)
    owners_str = remove_from_list(owners, email)
    update_classes_row(class_id, 'owner_email', owners_str)
    # demote from teacher role too
    if (not leave_as_teacher):
        demote_teacher(class_id, email)



def remove_member(class_id, email, purge_posts=False):
    # remove email from class owners list
    if (is_class_owner(class_id, email)):
        class_owners = get_class_owners(class_id)
        new_class_owners = remove_from_list(class_owners, email)
        update_classes_row(class_id, 'owner_email', new_class_owners)
    # remove email from class teachers list
    if (is_class_teacher(class_id, email)):
        class_teachers = get_class_teachers(class_id)
        new_class_teachers = remove_from_list(class_teachers, email)
        update_classes_row(class_id, 'teacher_email', new_class_teachers)
    # remove email from class members list
    class_members = get_class_members(class_id)
    new_class_members = remove_from_list(class_members, email)
    update_classes_row(class_id, 'member_email', new_class_members)
    # remove class from users class list
    user_classes = get_user_classes(email)
    new_user_classes = remove_from_list(user_classes, class_id)
    update_users_row(email, 'class_id', new_user_classes)
    # remove posts from this class in the user's table
    posts = get_class_posts(class_id)
    for post in posts:
        mark_read(email, post)
    # purge posts from this user if specified
    if (purge_posts):
        delete_class_posts_by(class_id, email)


def ban_member(class_id, email, purge_posts=False):
    remove_member(class_id, email, purge_posts)
    banned = get_banned_members(class_id)
    banned_str = add_to_list(banned, email)
    update_classes_row(class_id, 'banned_email', banned_str)




#---------[classes-helpers]---------#


def get_classes_field(class_id, field_name):
    return get_field('classes', 'class_id', class_id, field_name)

def add_classes_row(values):
    add_row('classes', values)

def update_classes_row(class_id, col_name, col_val):
    update_row('classes', 'class_id', class_id, col_name, col_val)




#=============================[POSTS]=============================#


#---------[accessors]---------#


def get_all_posts():
    data = get_col('posts', 'post_id')
    data = sort_by_ctime(data)
    return data

def get_posts_by(email):
    posts = get_all_posts()
    return [post for post in posts if get_post_author(post) == email]

def get_all_announcements():
    posts = get_all_posts()
    return [post for post in posts if get_post_category(post) == 'announcement']

def get_announcements_by(email):
    return [post for post in get_all_announcements() if get_post_author(post) == email]

def get_all_questions():
    posts = get_all_posts()
    return [post for post in posts if get_post_category(post) == 'question']

def get_questions_by(email):
    return [post for post in get_all_quesetions() if get_post_author(post) == email]

def get_all_notes():
    posts = get_all_posts()
    return [post for post in posts if get_post_category(post) == 'note']

def get_notes_by(email):
    return [post for post in get_all_notes() if get_post_author(post) == email]


def get_all_unresolved():
    return [post for post in get_all_questions() if not post_is_resolved(post)]

def get_unresolved_posts(class_id):
    return [post for post in get_all_unresolved() if get_post_class(post) == class_id]



# returns a dictionary of different types of followups
def get_post_followups(post_id):
    responses = [post for post in get_all_posts() if get_post_parent(post) == post_id]
    followups = {}
    # don't order these posts at all if these are followups to followups--leave a thread ordered by post creation time
    if (get_post_depth(post_id) > 0 or len(responses) == 0):
        responses = sort_by_ctime(responses)
        responses.reverse()
        followups['answers'] = []
        followups['teacher_responses'] = []
        followups['other'] = responses
        return followups
    teacher_answers = []
    answers = []
    teacher_responses = []
    other = []
    for post in responses:
        if post_is_answer(post):
            if is_class_teacher(get_post_class(post), get_post_author(post)):
                teacher_answers += [post]
            else:
                answers += [post]
        elif is_class_teacher(get_post_class(post), get_post_author(post)):
            teacher_responses += [post]
        else:
            other += [post]
    teacher_answers = order_by_upvotes(teacher_answers)
    answers = order_by_upvotes(answers)
    answers = teacher_answers + answers
    followups['answers'] = answers
    teacher_responses = order_by_upvotes(teacher_responses)
    followups['teacher_responses'] = teacher_responses
    other = order_by_upvotes(other)
    followups['other'] = other
    return followups


def get_post_depth(post_id):
    depth = 0
    post = post_id
    parent = get_post_parent(post_id)
    while str(parent) != 'None':
        depth += 1
        parent = get_post_parent(parent)
    return depth



def get_post_author(post_id):
    return get_posts_field(post_id, 'author_email')

def get_post_parent(post_id):
    return get_posts_field(post_id, 'parent_id')

def get_top_parent(post_id):
    parent = get_post_parent(post_id)
    if (str(parent) == 'None' or parent == ''):
        return post_id
    grandparent = get_post_parent(parent)
    if (str(grandparent) == 'None' or grandparent == ''):
        return parent
    return grandparent



def get_post_class(post_id):
    return get_posts_field(post_id, 'class_id')

def get_post_category(post_id):
    return get_posts_field(post_id, 'category')



def get_post_title(post_id):
    return get_posts_field(post_id, 'title')

def get_post_body(post_id):
    return get_posts_field(post_id, 'body')

def get_post_attachments(post_id):
    attachments = get_posts_field(post_id, 'attachments')
    return make_list(attachments)



def post_is_resolved(post_id):
    is_resolved = get_posts_field(post_id, 'is_resolved')
    return is_resolved == 'yes'

def post_is_answer(post_id):
    is_answer = get_posts_field(post_id, 'is_answer')
    return is_answer == 'yes'

def show_dojo(post_id):
    dojo_sees = get_posts_field(post_id, 'show_dojo')
    return dojo_sees == 'yes'



def get_post_ctime(post_id):
    return get_posts_field(post_id, 'created_at')

def get_post_utime(post_id):
    return get_posts_field(post_id, 'updated_at')



def get_post_upvotes(post_id):
    return get_posts_field(post_id, 'upvotes')

def get_post_upvoters(post_id):
    upvoters = get_posts_field(post_id, 'upvoters')
    upvoters_lst = make_list(upvoters)
    return upvoters_lst

def get_post_pingees(post_id):
    ping = get_posts_field(post_id, 'ping')
    ping_lst = make_list(ping)
    # remove users who have been deleted since the last time this list was accessed
    ping_filtered = [user for user in ping_lst if user_exists(user)]
    ping_str = merge_list(ping_filtered)
    update_posts_row(post_id, 'ping', ping_str)
    return ping_filtered



def get_post_data(post_id):
    keys = POSTS_COLS
    values = get_row('posts', 'post_id', post_id)
    d = list_to_dict(keys, values)
    d['attachments'] = make_list(d['attachments'])
    d['upvoters'] = make_list(d['upvoters'])
    d['ping'] = make_list(d['ping'])
    return d



#---------[modifiers]---------#



def change_post_title(post_id, new_title):
    update_posts_row(post_id, 'title', new_title)
    update_post_time(post_id)

def change_post_body(post_id, new_body):
    update_posts_row(post_id, 'body', new_body)
    update_post_time(post_id)



def resolve_post(post_id):
    update_posts_row(post_id, 'is_resolved', 'yes')

def unresolve_post(post_id):
    update_posts_row(post_id, 'is_resolved', 'no')



def mark_post_as_answer(post_id):
    update_posts_row(post_id, 'is_answer', 'yes')

def unmark_post_as_answer(post_id):
    update_posts_row(post_id, 'is_answer', 'no')



def update_post_time(post_id):
    time = str(datetime.now())
    update_posts_row(post_id, 'updated_at', time)



def increment_post_upvotes(post_id, inc):     # inc can be positive or negative
    upvotes = get_post_upvotes(post_id)
    upvotes += inc
    update_posts_row(post_id, 'upvotes', upvotes)

def add_post_upvoter(post_id, email):
    upvoters = get_post_upvoters(post_id)
    upvoters_new = add_to_list(upvoters, email)
    update_posts_row(post_id, 'upvoters', upvoters_new)
    increment_post_upvotes(post_id, 1)
    add_post_pingee(post_id, email)

def remove_post_upvoter(post_id, email):
    upvoters = get_post_upvoters(post_id)
    upvoters.remove(email)
    upvoters_new = merge_list(upvoters)
    update_posts_row(post_id, 'upvoters', upvoters_new)
    increment_post_upvotes(post_id, -1)
    remove_post_pingee(post_id, email)



def add_post_pingee(post_id, email):
    pingees = get_post_pingees(post_id)
    if email not in pingees:
        pingees_new = add_to_list(pingees, email)
        update_posts_row(post_id, 'ping', pingees_new)

def remove_post_pingee(post_id, email):
    author = get_post_author(post_id)
    if author != email:
        pingees = get_post_pingees(post_id)
        pingees.remove(email)
        pingees_new = merge_list(pingees)
        update_posts_row(post_id, 'ping', pingees_new)

def ping(post_id, pingees=[]):
    if len(pingees) == 0:
        pingees = get_post_pingees(post_id)
    for user in pingees:
        if not user_exists(user):
            remove_users += [user]
        else:
            pinged_posts = get_pinged_posts(user)
            pinged_str = add_to_list(pinged_posts, post_id)
            update_users_row(user, 'pinged_posts', pinged_str)


# decide to share post to dojo after post has already been created (this action cannot be undone)
def share_to_dojo(post_id):
    readers = get_all_dojo()
    for reader in readers:
        unread = get_unread_posts(reader)
        unread_str = add_to_list(unread, ping_post)
        update_users_row(reader, 'unread_posts', unread_str)
    update_posts_row(post_id, 'show_dojo', 'yes')



#---------[creation-deletion]---------#


def create_post(author_email, class_id, title, body, category, show_dojo, attachments='', is_anonymous='no', parent_id=''):
    post_id = gen_id(get_all_posts(), 16)
    is_resolved = 'no'
    is_answer = 'no'
    time = str(datetime.now())
    upvotes = 0
    upvoters = ''
    to_ping = author_email
    add_posts_row([post_id, author_email, class_id, parent_id, title, body, attachments, category, is_resolved, is_answer, time, time, upvotes, upvoters, to_ping, show_dojo, is_anonymous])
    ping_post = get_top_parent(post_id)
    # add to classes table
    class_posts = get_class_posts(class_id)
    posts_str = add_to_list(class_posts, ping_post)
    update_classes_row(class_id, 'posts', posts_str)
    # add as unread post
    readers = get_class_members(class_id)
    if (show_dojo == 'yes'):
        readers += get_all_dojo()
    readers = unique_only(readers)
    if author_email in readers:
        readers.remove(author_email)
    for reader in readers:
        unread = get_unread_posts(reader)
        unread_str = add_to_list(unread, ping_post)
        update_users_row(reader, 'unread_posts', unread_str)
    # ping necessary people
    if (parent_id != ''):
        ping(parent_id)
        add_post_pingee(parent_id, author_email)
    elif get_post_category(post_id) == 'announcement':
        ping_list = get_class_members(class_id)
        if (show_dojo == 'yes'):
            ping_list += get_all_dojo()
        ping_list = unique_only(ping_list)
        ping_list.remove(author_email)
        ping(post_id, ping_list)
    return post_id

def create_followup(author_email, post_id, body, is_anonymous='no'):
    followup_id = gen_id(get_all_posts(), 16)
    class_id = get_post_class(post_id)
    category = get_post_category(post_id)
    show_dojo = get_posts_field(post_id, 'show_dojo')
    is_resolved = 'no'
    is_answer = 'no'
    time = str(datetime.now())
    upvotes = 0
    upvoters = ''
    ping = author_email
    add_posts_row([followup_id, author_email, class_id, post_id, '', body, '', category, is_resolved, is_answer, time, time, upvotes, upvoters, ping, show_dojo, is_anonymous])
    return followup_id

def delete_post(post_id):
    # remove followups
    followups_dict = get_post_followups(post_id)
    followups = followups_dict['answers'] + followups_dict['teacher_responses'] + followups_dict['other']
    for f in followups:
        delete_post(f)
    delete_post_trace(post_id)

# delete all posts/followups in this class by this person
def delete_class_posts_by(class_id, email):
    posts = filter_by_class(get_posts_by(email), class_id)
    for post in posts:
        delete_post(post_id)



#---------[posts-helpers]---------#


def filter_by_class(posts, class_id):
    return [post for post in posts if get_post_class(post_id) == class_id]


def order_by_upvotes(posts):
    upvotes = [get_post_upvotes(post) for post in posts]
    ordered = []
    num_posts = len(posts)
    for i in range(num_posts):
        max_ind = 0
        max_val = upvotes[0]
        for j in range(1, len(posts)):
            if upvotes[j] > max_val:
                max_ind = j
                max_val = upvotes[j]
        ordered += [posts[max_ind]]
        posts.pop(max_ind)
        upvotes.pop(max_ind)
    return ordered


# deletes all traces of a post from all tables
def delete_post_trace(post_id):
    # remove from classes table
    class_id = get_post_class(post_id)
    class_posts = get_class_posts(class_id)
    c_posts_str = remove_from_list(class_posts, post_id)
    update_classes_row(class_id, 'posts', c_posts_str)
    # remove from users table
    readers = get_class_members(class_id)
    if (show_dojo(post_id)):
        readers += get_all_dojo()
    readers = unique_only(readers)
    for reader in readers:
        mark_read(reader, post_id)    # removes the post from unread/ping
    # remove from posts table
    delete_row('posts', 'post_id', post_id)


# sorts so that the most recent posts come first
def sort_by_ctime(posts):
    times = []
    sorted = []
    for post in posts:
        ctime = datetime.strptime(get_post_ctime(post), "%Y-%m-%d %H:%M:%S.%f")
        ind = 0
        while len(times) > ind and times[ind] >= ctime:
            ind += 1
        times.insert(ind, ctime)
        sorted.insert(ind, post)
    return sorted



def get_posts_field(post_id, field_name):
    return get_field('posts', 'post_id', post_id, field_name)

def add_posts_row(values):
    add_row('posts', values)

def update_posts_row(post_id, col_name, col_val):
    update_row('posts', 'post_id', post_id, col_name, col_val)




#=============================[GENERAL=HELPERS]=============================#


#---------[access]---------#


# return one value from the table based on another value in that row (an "id")
def get_field(table, ID_fieldname, ID, field):
    lst = get_field_list(table, ID_fieldname, ID, field)
    if (len(lst) == 0):
        return 'None'
    return lst[0]

# return all values in a specific field (column) in a row with a matching "id" item
def get_field_list(table, col_name, ID, field):
    # # use ? for user-provided, potentially unsafe values
    data = sqlite_fetchall(f'SELECT {field} FROM {table} WHERE {col_name} = ?', (ID,))
    return clean_list(data)

# return the first row that has an "id" field matching the given argument
def get_row(table, col_name, ID):
    return get_row_list(table, col_name, ID)[0]

# return all rows that have an "id" field matching the given argument
def get_row_list(table, col_name, ID):
    # # use ? for user-provided, potentially unsafe values
    data = sqlite_fetchall(f'SELECT * FROM {table} WHERE {col_name} = ?', (ID,))
    return clean_2d_list(data)

# return a list of all items in a column of the table
def get_col(table, col_name):
    # no unsafe/user-provided vars here, safe to use f-strings
    data = sqlite_fetchall(f'SELECT {col_name} FROM {table}')
    return clean_list(data)




#---------[modify]---------#


def add_row(table, vals):
    command = f'INSERT INTO {table} VALUES ('
    for i in range(len(vals)):
        command += '?,'
    command = command[:-1]
    command += ')'
    vals_tup= tuple(vals)
    sqlite(command, vals_tup)

def update_row(table, ID_fieldname, id, col_name, item):
    command = f'UPDATE {table} SET {col_name} = ? WHERE {ID_fieldname} = ?'
    vals = [item, id]
    vals_tup = tuple(vals)
    sqlite(command, vals_tup)

def delete_row(table, ID_fieldname, id):
    # # use ? for user-provided, potentially unsafe values
    sqlite(f'DELETE FROM {table} WHERE {ID_fieldname} = ?', (id,))



#---------[db-list-management]---------#


# PURPOSE
# Convert lists to/from delim-separated strings--we work with lists but store strings.

# PARAMETERS
# lst/str           LIST-STRINGS or STRING              The list/string to convert.
# delim             STRING                              An optional delimeter; defaults to ','.

# RETURN VALUES
# merge_list() returns a delim-separated string.
# make_list() returns a list.


# list -> comma (or some specified other delimeter)-separated string
def merge_list(lst, delim=','):
    if lst == None:
        return ''
    lst = rm_empty(lst)
    if lst == None:
        return ''
    return delim.join(lst)

# string of comma (or some specified other delimeter)-separated items -> list
def make_list(str, delim=','):
    if str == None:
        return []
    lst = str.split(delim)
    return rm_empty(lst)



# PURPOSE
# Add or remove an item from a list and convert the list into a delim-separated string.

# PARAMETERS
# lst               LIST-STRINGS or STRING              A list of items or a delim-separated string of items.
# item              STRING                              The item to add or remove.
# delim             STRING                              An optional delimeter; defaults to ','.          

# RETURN VALUES
# add_to_list() returns a delim-separated string with item appended.
# remove_from_list() returns a delim-separated string with (the first instance of) item removed.


# add an item to a list and return a delim-separated string
def add_to_list(lst, item, delim=','):
    # check if lst has been provided as a list already or if we need to convert it into one
    if isinstance(lst, str):
        lst = make_list(lst, delim)
    lst += [item]
    # make this into a delim-separated string for our database
    new_str = merge_list(lst, delim)
    return new_str

# remove (the first instance of) an item from a list and return a delim-separated string
def remove_from_list(lst, item, delim=','):
    # check if lst has been provided as a list already or if we need to convert it into one
    if isinstance(lst, str):
        lst = make_list(lst, delim)
    if item in lst:
        lst.remove(item)
    # make this into a delim-separated string for our database
    new_str = merge_list(lst, delim)
    return new_str



# PURPOSE
# Return a list that only contains the unique values of the inputted list.

# PARAMETERS
# lst               LIST-ANY                            A list of any items.

# RETURN VALUES
# unique_only() returns a list of unique items.


# keep only unique items in the list
def unique_only(lst):
    new_lst = []
    for item in lst:
        if item not in new_lst:
            new_lst += [item]
    return new_lst


#---------[id]---------#


# PURPOSE
# Generate a unique id whenever needed.

# PARAMETERS
# others            LIST-STRINGS                        A list of previously used ids.
# byte_nums         INTEGER                             The number of bytes the id should take up.

# RETURN VALUES
# gen_id() returns a an alphanumeric string.


def gen_id(others, byte_nums):
    # generate an id
    id = secrets.token_hex(byte_nums)
    # make sure it's unique
    while id in others:
        id = secrets.token_hex(byte_nums)
    return id


#---------[output-convert]---------#


# PURPOSE
# Convert plain lists into dictionaries, given a list of corresponding keys.

# PARAMETERS
# keys              LIST-STRINGS                                    A list of keys corresponding to the provided list of values.
# values            LIST-STRINGS or LIST-LIST-STRINGS               A list (or list of lists) of values corresponding to the provided list of keys.

# RETURN VALUES
# Use list_to_dict() to get a dictionary.
# Use list_2d_to_dict_list to get a list of dictionaries.


# list of keys + list of values -> dictionary
def list_to_dict(keys, values):
    if len(keys) != len(values):
        print("list_to_dict: len keys != len values")
        return {}
    dict = {}
    for i in range(len(keys)):
        dict[keys[i]] = values[i]
    return dict

# list of keys + 2d list of values -> list of dictionaries
def list_2d_to_dict_list(keys, values):
    lst = []
    for val_sublst in values:
        lst += [list_to_dict(keys, val_sublst)]
    return lst



# PURPOSE
# Convert a list of tuples (which is what is returned by .fetchall()) into lists to work with.
# Either create a 1d list or a 2d list.

# PARAMETERS
# raw_output        LIST-TUPLES             A list of tuples fetched as the result of a SQLite3 command.

# RETURN VALUES
# Use tups_to_list for a 1d list.
# Use tups_to_list_2d for a 2d list.


# list of tuples (returned by .fetchall()) -> 1d list
def tups_to_list(raw_output):
    lst = []
    for tup in raw_output:
        # represent None as '', otherwise add item to list as is
        lst += ['' if item is None else item for item in tup]
    return lst

# list of tuples (returned by .fetchall()) -> 2d list
def tups_to_2d_list(raw_output):
    lst = []
    for tup in raw_output:
        sub_lst = list(tup)
        # represent None as '', otherwise add item to list as is
        sub_lst = ['' if item is None else item for item in sub_lst]
        lst += [sub_lst]
    return lst



# PURPOSE
# Convert a list of tuples (which is what is returned by .fetchall()) into FILTERED lists to work with.
# Either create a 1d list or a 2d list.

# PARAMETERS
# raw_output       LIST-TUPLES          A list of tuples fetched as the result of a SQLite3 command.

# RETURN VALUES
# Use clean_list() for a 1d list without any empty items ('').
# Use clean_2d_list() for a 2d list without any empty sub_lists--but sub_lists may contain ''.
# Use deep_clean_list() for a 2d list without any empty sub_lists--sub_lists will NOT contain ''.


# turn a list of tuples (returned by .fetchall()) into a 1d list AND remove empty items
def clean_list(raw_output):
    clean_output = tups_to_lst(raw_output)
    clean_output = rm_empty(raw_output)
    return clean_output

# turn a list of tuples (returned by .fetchall()) into a 2d list AND remove empty 1d lists
def clean_2d_list(raw_output):
    clean_output = tups_to_2d_lst(raw_output)
    clean_output = rm_empty_lists(clean_output)
    return clean_output

# turn a list of tuples (returned by .fetchall()) into a 2d list AND remove empty 1d lists AND remove empty items from each sub-list
def deep_clean_list(raw_output):
    clean_output = tups_to_2d_list(raw_output)
    clean_output = deep_rm_empty(clean_output)
    return clean_output



# PURPOSE
# Remove empty entries ('' or []) from lists.

# PARAMETERS
# lst(_2d)      LIST-STRINGS or LIST-LIST-STRINGS       The list to remove empty entries from.

# RETURN VALUES
# Use rm_empty() to remove '' from 1d lists.
# Use rm_empty_lists() to remove [] from 2d lists.
# Use deep_rm_empty() to remove [] from 2d lists AND remove '' from each sub_list.


# remove '' and None from a 1d list
def rm_empty(lst):
    clean_lst = [item for item in lst if item is not None and item != '']
    if (clean_lst is None):
        clean_lst = []
    return clean_lst

# remove [] from a 2d list
def rm_empty_lists(lst_2d):
    clean_lst = [lst for lst in lst_2d if len(lst) > 0]
    return clean_lst

# remove [] from a 2d lists AND remove None/'' from each sub_list
def deep_rm_empty(lst_2d):
    new_lst = rm_empty_lists(lst_2d)
    for i in range(len(new_lst)):
        sub_lst = new_lst[i]
        new_lst[i] = rm_empty(sub_lst)
    return new_lst



#---------[sqlite]---------#

# PURPOSE
# These helper functions serve to interact directly with SQLite3.

# PARAMETERS
# command       STRING          A command for SQLite3 to execute.
# vals          TUPLE           An OPTIONAL tuple of values that are filtered (in case of SQL injection), then added to the command.

# RETURN VALUES
# Use sqlite() for commands that return nothing.
# Use sqlite_fetchone() if you are looking for one piece of data from the dataset.
# Use sqlite_fetchall() to run commands that return a list of tuples (a lot of data).


# run a command that returns nothing in SQLite3
def sqlite(command, vals=()):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    if vals == ():
        c.execute(command)
    else:
        c.execute(command, vals)
    db.commit()
    db.close()


# run a SQLite3 command and get the result (one tuple of data)
def sqlite_fetchone(command, vals=()):
    return sqlite_fetchall(command, vals)[0]


# run a SQLite3 command and get the result (a list of tuples of data)
def sqlite_fetchall(command, vals=()):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    data = ()
    if vals == ():
        data = c.execute(command).fetchall()
    else:
        data = c.execute(command, vals).fetchall()
    db.commit()
    db.close()
    return data





#=============================[TESTING]=============================#

if __name__ == "__main__":

    create_tables()

    add_user("mayaberchin@gmail.com", "hello", "Maya Berchin")
    add_user("other@gmail.com", "other", "Other Student")
    #print(str(get_all_users()))
    add_user("b@b.com", "b", "b b")

    #print(str(get_all_classes()))
    class_id = create_class("mayaberchin@gmail.com", "testclass")
    create_class("b@b.com", "dontjoin")
    print(class_id)
    #print("\n" + str(get_all_classes()))
    #print("Class teachers: " + str(get_class_teachers(class_id)))

    add_class_member(class_id, "other@gmail.com")

    print("\nClasses Maya is in: " + str(get_user_classes("mayaberchin@gmail.com")))
    print("Classes Maya teaches: " + str(get_teaching_classes("mayaberchin@gmail.com")))
    print("Classes Other is in: " + str(get_user_classes("other@gmail.com")))
    print("Classes Other teaches: " + str(get_teaching_classes("other@gmail.com")))


    #print("\nPromoting Other... also removing Maya as owner")
    promote_to_owner(class_id, 'other@gmail.com')
    demote_owner(class_id, "mayaberchin@gmail.com")

    print("Class teachers: " + str(get_class_teachers(class_id)))
    print("Classes Maya is in: " + str(get_user_classes("mayaberchin@gmail.com")))
    print("Classes Maya teaches: " + str(get_teaching_classes("mayaberchin@gmail.com")))
    print("Classes Other is in: " + str(get_user_classes("other@gmail.com")))
    print("Classes Other teaches: " + str(get_teaching_classes("other@gmail.com")))
    print("Classes Maya owns: " + str(get_owned_classes("mayaberchin@gmail.com")))
    print("Classes Other owns: " + str(get_owned_classes("other@gmail.com")))


    for i in range(15):
        add_user(f"{i}@gmail.com", "b", "b b")
        add_class_member(class_id, f'{i}@gmail.com')
    #print(str(get_class_members(class_id)))
    add_user("16@gmail.com", "b", "b b")
    add_user("17@gmail.com", "b", "b b")
    add_user("18@gmail.com", "b", "b b")
    add_class_member(class_id, '16@gmail.com')
    ban_member(class_id, '1@gmail.com')
    add_class_member(class_id, '17@gmail.com')
    #print(str(get_class_members(class_id)))
    add_class_member(class_id, '1@gmail.com')
    add_class_member(class_id, '18@gmail.com')
    #print(str(get_class_members(class_id)))
    change_class_name(class_id, "testingagain!")
    #print(get_class_name(class_id))
    archive_class(class_id)
    #print(str(get_active_classes()))
    un_archive_class(class_id)
    #print(str(get_active_classes()))

    #print("\n")
    #print(str(get_all_posts()))
    #delete_class(class_id)

    print(str(get_all_classes()))
    print("Classes Maya is in: " + str(get_user_classes("mayaberchin@gmail.com")))
    print("Classes Maya teaches: " + str(get_teaching_classes("mayaberchin@gmail.com")))
    print("Classes Other is in: " + str(get_user_classes("other@gmail.com")))
    print("Classes Other teaches: " + str(get_teaching_classes("other@gmail.com")))
    print("Classes Maya owns: " + str(get_owned_classes("mayaberchin@gmail.com")))
    print("Classes Other owns: " + str(get_owned_classes("other@gmail.com")))
    print(str(get_all_posts()))



    print("\n----------------------------------\n")
    # author_email, class_id, title, body, category, show_dojo, attachments='', is_anonymous='no', parent_id=''
    post_id = create_post("mayaberchin@gmail.com", class_id, "test_post", "this is the body of the test post", "question", "no")
    print(get_all_posts())
    print(str(get_post_data(post_id)))
    add_post_upvoter(post_id, "other@gmail.com")
    change_post_title(post_id, "test title 2")
    resolve_post(post_id)
    print(str(get_post_data(post_id)))
    unresolve_post(post_id)
    remove_post_upvoter(post_id, "other@gmail.com")
    add_post_upvoter(post_id, "b@b.com")
    share_to_dojo(post_id)
    print(str(get_post_data(post_id)))


    announcement_id = create_post("mayaberchin@gmail.com", class_id, "ann", "important announcement!", "announcement", "no")
    print("\n")
    print(announcement_id)
    print(str(get_unread_posts('0@gmail.com')))
    print(str(get_pinged_posts('0@gmail.com')))
    print(str(get_unresolved_posts(class_id)))

    create_followup('b@b.com', announcement_id, "huhhh???")
    create_followup('0@gmail.com', announcement_id, "lolll i get it")
    f_id = create_followup('0@gmail.com', announcement_id, ":)")
    print("parent: " + get_post_parent(f_id))
    add_post_upvoter(f_id, "b@b.com")
    fs = get_post_followups(announcement_id)['other']
    for f in fs:
        print(get_post_body(f))
    ff_id = create_followup('0@gmail.com', f_id, "double followup")
    ff_id = create_followup('0@gmail.com', f_id, "bleh")
    add_post_upvoter(ff_id, "b@b.com")
    ffs = get_post_followups(f_id)['other']
    for ff in ffs:
        print(get_post_body(ff))

    lst = get_teacher_head_posts(class_id)
    for item in lst:
        print(get_post_body(item))

    change_post_body(announcement_id, "nvm")
    print(str(get_post_data(announcement_id)))

    '''
    print("\n----------------------------------\n")
    add_senpai("mayaberchin@gmail.com")
    print(str(get_all_dojo()))
    '''
