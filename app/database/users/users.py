import hashlib                              # for consistent hashes
from datetime import datetime               # for dates/times

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
    d['classes'] = helpers.make_list(d['classes'])
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
    classes = ''
    unread_posts = ''
    pinged_posts = ''
    add_users_row([email, github, name, password, is_dojo, is_sensei, is_stuy_teacher, classes, unread_posts, pinged_posts])
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



#=====================================================[TABLE-HELPERS]=====================================================#



                                            #---------[accessors]---------#


# PURPOSE
# These helper functions serve to access data from the 'users' table.
# They correspond to more general functions in tables.py--these are basically wrappers.

# PARAMETERS
# email         STRING          The email corresponding to the entry (row) containing data we want to access.
# field_name    STRING          The name of the field (column) containing the data of interest to us.
# col_name      STRING          The name of the entire column we are getting from the table.

# RETURN VALUES
# get_users_field() returns the first piece of data from 'users' that matches the criteria.
# get_users_field_list() returns a list of all data from 'users' that matches the criteria.
# get_users_row() returns the first row from 'users' that matches the criteria, formatted as a list.
# get_users_row_list() returns a list of all rows from 'users' that match the criteria, formatted as a 2d list.
# get_users_col() returns data from an entire column of 'users' formatted as a list.


def get_users_field(email, field_name):
    return helpers.get_field('users', 'email', email, field_name)

def get_users_field_list(email, field_name):
    return helpers.get_field_list('users', 'email', email, field_name)

def get_users_row(email):
    return tables.get_row('users', 'email', email)

def get_users_row_list(email):
    return tables.get_row_list('users', 'email', email)

def get_users_col(col_name):
    return tables.get_col('users', col_name)




                                            #---------[modifiers]---------#


# PURPOSE
# These helper functions serve to modify data in the 'users' table.
# They correspond to more general functions in tables.py--these are basically wrappers.

# PARAMETERS
# email         STRING                          The email corresponding to the entry (row) containing data we want to modify.
# col_name      STRING                          The name of the field (column) containing data we want to modify.
# value(s)      STRING or LIST-STRING           The new data we want to put in the table (add or update).

# RETURN VALUES
# None of these functions return anything.


def add_users_row(values):
    tables.add_row('users', values)

def update_users_row(email, col_name, value):
    tables.update_row('users', 'email', email, col_name, value)

def delete_users_row(email):
    tables.delete_row('users', 'email', email)