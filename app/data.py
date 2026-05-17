import sqlite3                      # enable control of an sqlite database
import hashlib                      # for consistent hashes
import secrets                      # to generate ids


DB_FILE="data.db"

#=============================[GLOBALS]=============================#

USERS_COLS = ['user_id', 'email', 'github', 'name', 'password_hash', 'is_dojo', 'class_id']
CLASSES_COLS = ['class_id', 'name', 'teacher_id']
POSTS_COLS = ['post_id', 'poster_id', 'class_id', 'title', 'body', 'category', 'status', 'created_at', 'updated_at', 'upvotes', 'upvoted_by', 'ping']
FOLLOWUPS_COLS = ['followup_id', 'poster_id', 'post_id', 'body', 'status', 'is_answer', 'created_at', 'updated_at', 'upvotes', 'upvoted_by', 'ping']

CLASS_ID = 0

#=============================[MAKE=TABLES]=============================#

# users
def create_users_table():
    command =  """
                CREATE TABLE IF NOT EXISTS users (
                    user_id         INTEGER     NOT NULL    PRIMARY KEY     AUTOINCREMENT,
                    email           TEXT        NOT NULL                    UNIQUE,
                    github          TEXT,
                    name            TEXT        NOT NULL,
                    password_hash   TEXT        NOT NULL,
                    is_dojo         TEXT        NOT NULL                                            DEFAULT 'no',
                    class_id        TEXT
                )"""
    sqlite(command)

# classes
def create_classes_table():
    command =  """
                CREATE TABLE IF NOT EXISTS classes (
                    class_id        INTEGER     NOT NULL    PRIMARY KEY     AUTOINCREMENT,
                    name            TEXT        NOT NULL,
                    teacher_id      TEXT        NOT NULL
                )"""
    sqlite(command)

# posts
def create_posts_table():
    command =  """
                CREATE TABLE IF NOT EXISTS posts (
                    post_id         INTEGER     NOT NULL    PRIMARY KEY     AUTOINCREMENT,
                    poster_id       INTEGER     NOT NULL,
                    class_id        INTEGER     NOT NULL,
                    title           TEXT        NOT NULL,
                    body            TEXT        NOT NULL,
                    category        TEXT        NOT NULL,
                    status          TEXT        NOT NULL,
                    created_at      TEXT        NOT NULL                                            DEFAULT CURRENT_TIMESTAMP,
                    updated_at      TEXT        NOT NULL                                            DEFAULT CURRENT_TIMESTAMP,
                    upvotes         INTEGER     NOT NULL,
                    upvoted_by      TEXT,
                    ping            TEXT
                )"""
    sqlite(command)

# followups
def create_followups_table():
    command =  """
                CREATE TABLE IF NOT EXISTS posts (
                    followup_id     INTEGER     NOT NULL    PRIMARY KEY     AUTOINCREMENT,
                    poster_id       INTEGER     NOT NULL,
                    post_id         INTEGER     NOT NULL,
                    body            TEXT        NOT NULL,
                    status          TEXT        NOT NULL,
                    is_answer       TEXT        NOT NULL                                            DEFAULT 'no',
                    created_at      TEXT        NOT NULL                                            DEFAULT CURRENT_TIMESTAMP,
                    updated_at      TEXT        NOT NULL                                            DEFAULT CURRENT_TIMESTAMP,
                    upvotes         INTEGER     NOT NULL,
                    upvoted_by      TEXT,
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


# returns a list of usernames
def get_all_users():
    #data = sqlite_fetchall('SELECT email FROM users')
    data = get_col_list("users", "email")
    return clean_list(data)


def get_id(email):
    data = get_field("users", "email", email, user_id)
    return data

def get_email(id):
    data = get_field("users", "user_id", id, "email")
    return data


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

    # use ? for unsafe/user provided variables
    #real_pass = sqlite_fetchone('SELECT password_hash FROM users WHERE email = ?', (email,))[0]
    real_pass = get_field("users", "email", email, "password_hash")
    password = password.encode('utf-8')

    # hash password here
    if real_pass != str(hashlib.sha256(password).hexdigest()):
        return False

    return True


# adds a new user's data to user table
def add_user(email, password, name, github=''):

    if user_exists(email):
        return 'There is already a user with this email'

    if password == "":
        return 'Password cannot be empty'

    # hash password here
    password = password.encode('utf-8')
    password = str(hashlib.sha256(password).hexdigest())

    # use ? for unsafe/user provided variables
    #sqlite('INSERT INTO users(email, github, name, password_hash, is_dojo, class_id) VALUES (?, ?, ?, ?, ?, ?)', (email, github, name, password, 'no', '',))
    add_row("users", USERS_COLS, [email, github, name, password, 'no', ''])

    return 'success'



#=============================[CLASSES]=============================#


def get_all_classes():
    #data = sqlite_fetchall('SELECT class_id FROM users')
    data = get_col_list("users", "class_id")
    return clean_list(data)

# get the classes someone is in
def get_classes(email):
    classes_str = get_field('users', 'email', email, 'class_id')
    classes = make_list(classes_str)
    return classes

# get the classes someone teaches 
def teaches_classes(email):
    classes = get_classes(email)
    teaches = [c for c in classes if c in get_teachers(c)]
    return teaches

# get the teachers of a class
def get_teachers(class_id):
    teachers_str = get_field('classes', 'class_id', class_id, 'teacher_id')
    teachers = make_list(classes_str)
    return teachers


def create_class(teacher_id, class_name):
    global CLASS_ID
    #sqlite('INSERT INTO classes(class_id, name, teacher_id) VALUES (?, ?, ?)', (teacher_id, class_name,))
    add_row('classes', CLASS_COLS, [teacher_id, class_name])
    CLASS_ID += 1
    teacher_classes = get_classes(get_email(teacher_id))
    teacher_classes += f', {CLASS_ID}'
    update_row('users', 'email', get_email(teacher_id), 'class_id', teacher_classes)

def join_class(email, class_id):
    classes = get_classes(email)
    classes += f', {class_id}'
    update_row('users', 'email', email, 'class_id', classes)


#=============================[GENERAL=HELPERS]=============================#


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




#---------[access]---------#


# get_field: return one value from the table based on another value in that row (an "id")
def get_field(table, ID_fieldname, ID, field):
    lst = get_field_list(table, ID_fieldname, ID, field)
    if (len(lst) == 0):
        return 'None'
    return lst[0]

# get_field_list: return all values in a specific field (column) in a row with a matching "id" item
def get_field_list(table, col_name, ID, field):
    # use ? for unsafe/user provided variables
    data = sqlite_fetchall(f'SELECT {field} FROM {table} WHERE {col_name} = ?', (ID,))
    return clean_list(data)

# get_row_list: return all rows that have an "id" field matching the given argument
def get_row_list(table, col_name, ID):
    # use ? for unsafe/user provided variables
    data = sqlite_fetchall(f'SELECT * FROM {table} WHERE {col_name} = ?', (ID,))
    return clean_list_2d(data)

# return a list of all items in a column of the table
def get_col_list(table, col_name):
    # no unsafe/user-provided vars here, safe to use f-strings
    data = sqlite_fetchall(f'SELECT {col_name} FROM {table}')
    return clean_list(data)




#---------[modify]---------#


def add_row(table, cols=[], vals):
    
    # 'INSERT INTO tablename(col0, col1, col2) VALUES (?, ?, ?)', (val0, val1, val2,)
    
    command = f'INSERT INTO {table}'
    
    if (cols != []):
        cols_str = str(cols)[1:-1]  # make a string of the list and don't include the '[' or ']'
        command += f'({cols_str})'
    
    q_str = ' VALUES ('
    for i in range(len(vals)):
        q_str += '?,'
    q_str(len(q_str)-1) = ')'
    command += q_str
    
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
    
    


#---------[other]---------#

# generate an id
def gen_id():
    # use secrets module to generate a random 32-byte string
    return secrets.token_hex(32)

# merge a list into a comma-separated (or some other delimeter) string
def merge_list(lst, delim=","):
    return delim.join(lst)

# return a list from a string of comma-separated items (or some other delimeter)
def make_list(str, delim=","):
    return str.split(delim)



#=============================[TESTING]=============================#

if __name__ == "__main__":
    create_tables()
    add_user("mayaberchin@gmail.com", "hello", "Maya Berchin")
