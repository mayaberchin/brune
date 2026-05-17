import sqlite3                      # enable control of an sqlite database
import hashlib                      # for consistent hashes
import secrets                      # to generate ids


DB_FILE="data.db"

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
                    class_id        TEXT
                )"""
    sqlite(command)

# classes
def create_classes_table():
    command =  """
                CREATE TABLE IF NOT EXISTS classes (
                    class_id        TEXT        NOT NULL    PRIMARY KEY,
                    name            TEXT        NOT NULL,
                    teacher_email   TEXT        NOT NULL
                )"""
    sqlite(command)

# posts
def create_posts_table():
    command =  """
                CREATE TABLE IF NOT EXISTS posts (
                    post_id         TEXT        NOT NULL    PRIMARY KEY,
                    poster_email    TEXT        NOT NULL,
                    class_id        TEXT        NOT NULL,
                    title           TEXT        NOT NULL,
                    body            TEXT        NOT NULL,
                    category        TEXT        NOT NULL,
                    resolved        TEXT        NOT NULL                                DEFAULT 'no',
                    created_at      TEXT        NOT NULL                                DEFAULT CURRENT_TIMESTAMP,
                    updated_at      TEXT        NOT NULL                                DEFAULT CURRENT_TIMESTAMP,
                    upvotes         INTEGER     NOT NULL,
                    upvoters        TEXT,
                    ping            TEXT
                )"""
    sqlite(command)

# followups
def create_followups_table():
    command =  """
                CREATE TABLE IF NOT EXISTS posts (
                    followup_id     TEXT        NOT NULL    PRIMARY KEY,
                    poster_email    TEXT        NOT NULL,
                    post_id         TEXT        NOT NULL,
                    body            TEXT        NOT NULL,
                    resolved        TEXT        NOT NULL                                DEFAULT 'no',
                    is_answer       TEXT        NOT NULL                                DEFAULT 'no',
                    created_at      TEXT        NOT NULL                                DEFAULT CURRENT_TIMESTAMP,
                    updated_at      TEXT        NOT NULL                                DEFAULT CURRENT_TIMESTAMP,
                    upvotes         INTEGER     NOT NULL,
                    upvoters        TEXT,
                    ping            TEXT
                )"""
    sqlite(command)


# all
def create_tables():
    create_users_table()
    create_classes_table()
    create_posts_table()
    create_followups_table()



#=============================[USERS]=============================#


#---------[accessors]---------#

# returns a list of usernames
def get_all_users():
    data = get_col("users", "email")
    return data




#---------[modifiers]---------#

# adds a new user's data to user table
def add_user(email, password, name, github=''):
    if user_exists(email):
        return 'There is already a user with this email'
    if password == "":
        return 'Password cannot be empty'
    password = password.encode('utf-8')
    password = str(hashlib.sha256(password).hexdigest())
    add_users_row([email, github, name, password, 'no', ''])
    return 'success'




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
    real_pass = get_users_field(email, 'password_hash')
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


#---------[class-focused-accessors]---------#


def get_all_classes():
    data = get_col('classes', 'class_id')
    return data

def get_name(class_id):
    return get_field('classes', 'class_id', class_id, 'name')

# get the teachers of a class
def get_teachers(class_id):
    teachers_str = get_field('classes', 'class_id', class_id, 'teacher_email')
    teachers = make_list(teachers_str)
    return teachers



#---------[member-focused-accessors]---------#


# get the classes someone is in
def get_classes(email):
    classes_str = get_field('users', 'email', email, 'class_id')
    classes = make_list(classes_str)
    return classes

# get the classes someone teaches 
def get_teaching_classes(email):
    classes = get_classes(email)
    teaches = [c for c in classes if email in get_teachers(c)]
    return teaches



#---------[class-creation]---------#


def create_class(teacher_email, class_name):
    # add the class to classes table
    class_id = unique_id(get_all_classes())
    add_classes_row([class_id, class_name, teacher_email])
    # add the class to teacher's users table
    teacher_classes = get_classes(teacher_email)
    teacher_classes += [class_id]
    teacher_classes_str = merge_list(teacher_classes)
    update_users_row(teacher_email, 'class_id', teacher_classes_str)
    return class_id
    

    
#---------[member-focused-modifiers]---------#


# add a user to a class as a student
def join_class(email, class_id):
    classes = get_classes(email)
    classes += [class_id]
    classes_str = merge_list(classes)
    update_users_row('users', 'email', email, 'class_id', classes_str)

# promote a class member to a teacher for that class
def add_teacher(class_id, email):
    teachers = get_teachers(class_id)
    teachers += [email]
    teachers_str = merge_list(teachers)
    update_classes_row(class_id, 'teacher_email', teachers_str)



#---------[classes-helpers]---------#


def get_classes_field(class_id, field_name):
    return get_field('classes', 'class_id', class_id, field_name)

def add_classes_row(values):
    add_row('classes', values)

def update_classes_row(class_id, col_name, col_val):
    update_row('classes', 'class_id', class_id, col_name, col_val)




#=============================[POSTS]=============================#


#---------[post-accessors]---------#

def get_all_posts():
    data = get_col('posts', 'post_id')
    return data

def get_post_author(post_id):
    return get_posts_field(post_id, 'poster_id')

def get_post_class(post_id):
    return get_posts_field(post_id, 'class_id')

def get_post_title(post_id):
    return get_posts_field(post_id, 'title')

def get_post_body(post_id):
    return get_posts_field(post_id, 'body')

def get_post_category(post_id):
    return get_posts_field(post_id, 'category')

def post_is_resolved(post_id):
    resolved = get_posts_field(post_id, 'resolved')
    return resolved == 'yes'

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
    return ping_lst




#---------[posts-helpers]---------#

def get_posts_field(post_id, field_name):
    return get_field('posts', 'post_id', post_id, field_name)

def get_posts_row(values):
    add_row('posts', values)

def update_posts_row(post_id, col_name, col_val):
    update_row('posts', 'post_id', post_id, col_name, col_val)



#=============================[FOLLOWUPS]=============================#


def get_all_followups():
    data = get_col('followups', 'followup_id')
    return data



#---------[posts-helpers]---------#

def get_followups_field(followup, field_name):
    return get_field('followups', 'followup_id', followup_id, field_name)

def get_followups_row(values):
    add_row('followups', values)

def update_followups_row(followup_id, col_name, col_val):
    update_row('followups', 'followup_id', followup_id, col_name, col_val)




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
    # use ? for unsafe/user provided variables
    data = sqlite_fetchall(f'SELECT {field} FROM {table} WHERE {col_name} = ?', (ID,))
    return clean_list(data)

# return all rows that have an "id" field matching the given argument
def get_row_list(table, col_name, ID):
    # use ? for unsafe/user provided variables
    data = sqlite_fetchall(f'SELECT * FROM {table} WHERE {col_name} = ?', (ID,))
    return clean_list_2d(data)

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
    # use ? for unsafe/user provided variables
    sqlite(f'DELETE FROM {table} WHERE {ID_fieldname} = ?', (id,))



#---------[db-list-management]---------#


# merge a list into a comma-separated (or some other delimeter) string
def merge_list(lst, delim=","):
    lst = rm_empty(lst)
    return delim.join(lst)

# return a list from a string of comma-separated items (or some other delimeter)
def make_list(str, delim=","):
    lst = str.split(delim)
    return rm_empty(lst)
    
    
    
    
#---------[id]---------#


def unique_id(others):
    id = gen_id()
    while id in others:
        id = gen_id()
    return id

# generate an id
def gen_id():
    # use secrets module to generate a random 3-byte string
    return secrets.token_hex(3)




#---------[output-convert]---------#


# turn a list of tuples (returned by .fetchall()) into a 1d list
def clean_list(raw_output):
    clean_output = []
    for lst in raw_output:
        for item in lst:
            if str(item) != 'None' and item != "":
                clean_output += [item]
    return clean_output


# turn a list of tuples (returned by .fetchall()) into a 2d list
def clean_list_2d(raw_output):
    clean_output = []
    for lst in raw_output:
        clean_1d = []
        for item in lst:
            if str(item) != 'None' and item != '':
                clean_1d += [item]
        if len(lst) > 0:
            clean_output += [lst]
    return clean_output


# convert a list of data into a dictionary
def list_to_dict(keys, values):
    if len(keys) != len(values):
        print("list_to_dict: length keys != length values")
        return {}
    dict = {}
    for i in range(len(keys)):
        dict[keys[i]] = values[i]
    return dict


# convert a 2d list of data to a list of dictionaries
def list_2d_to_dict_list(keys, values):
    lst = []
    for val_sublst in values:
        lst += [list_to_dict(keys, val_sublst)]
    return lsta

# remove empty and none from a 1d list
def rm_empty(lst):
    cleanlst = [item for item in lst if str(item) != 'None' and item != '']
    return cleanlst
    



#---------[sqlite]---------#


def sqlite(command, vals=()):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    if vals == ():
        c.execute(command)
    else:
        c.execute(command, vals)
    db.commit()
    db.close()


def sqlite_fetchone(command, vals=()):
    return sqlite_fetchall(command, vals)[0]


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
    print(str(get_all_users()))
    add_user("b@b.com", "b", "b b")
    
    print(str(get_all_classes()))
    class_id = create_class("mayaberchin@gmail.com", "testclass")
    create_class("b@b.com", "dontjoin")
    print("\n" + str(get_all_classes()))
    print("Class teachers: " + str(get_teachers(class_id)))
    
    join_class("other@gmail.com", class_id)
    print("\nClasses Maya is in: " + str(get_classes("mayaberchin@gmail.com")))
    print("Classes Maya teaches: " + str(get_teaching_classes("mayaberchin@gmail.com")))
    print("Classes Other is in: " + str(get_classes("other@gmail.com")))
    print("Classes Other teaches: " + str(get_teaching_classes("other@gmail.com")))
    
    print("\nPromoting Other...")
    add_teacher(class_id, 'other@gmail.com')
    print("Class teachers: " + str(get_teachers(class_id)))
    print("Classes Maya is in: " + str(get_classes("mayaberchin@gmail.com")))
    print("Classes Maya teaches: " + str(get_teaching_classes("mayaberchin@gmaill.com")))
    print("Classes Other is in: " + str(get_classes("other@gmail.com")))
    print("Classes Other teaches: " + str(get_teaching_classes("other@gmail.com")))