import sqlite3                      # enable control of an sqlite database
import hashlib                      # for consistent hashes
import secrets                      # to generate ids


DB_FILE="data.db"

#=============================[MAKE=TABLES]=============================#

# users
def create_users_table():
    command =  """
                CREATE TABLE IF NOT EXISTS users (
                    user_id         INTEGER     NOT NULL    PRIMARY KEY     AUTOINCREMENT,
                    email           TEXT        NOT NULL                    UNIQUE,
                    github          TEXT                                    UNIQUE,
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


#=============================[USERS]=============================#


# returns a list of usernames
def get_all_users():

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    data = c.execute('SELECT username FROM users').fetchall()

    db.commit()
    db.close()

    return clean_list(data)


# returns whether or not a user exists
def user_exists(username):
    all_users = get_all_users()
    for user in all_users:
        if (user == username):
            return True
    return False


# checks if provided password in login attempt matches user password
def auth(username, password):

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    if not user_exists(username):
        db.commit()
        db.close()

        #raise ValueError("Username does not exist")
        return False

    # use ? for unsafe/user provided variables
    passpointer = c.execute('SELECT password FROM users WHERE username = ?', (username,))
    real_pass = passpointer.fetchone()[0]

    db.commit()
    db.close()

    password = password.encode('utf-8')

    # hash password here
    if real_pass != str(hashlib.sha256(password).hexdigest()):
        #raise ValueError("Incorrect password")
        return False

    return True


# adds a new user's data to user table
def add_user(username, password):

    if user_exists(username):
        #raise ValueError("Username already exists")
        return "Username already exists"

    if password == "":
        #raise ValueError("You must enter a non-empty password")
        return "Password cannot be empty"

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # hash password here
    password = password.encode('utf-8')
    password = str(hashlib.sha256(password).hexdigest())

    # use ? for unsafe/user provided variables
    c.execute('INSERT INTO users VALUES (?, ?)', (username, password,))

    db.commit()
    db.close()

    return "success"



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
    return lst




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


# delete_row: delete a row of data from the table
def delete_row(table, ID_fieldname, id):
    # use ? for unsafe/user provided variables
    sqlite(f'DELETE FROM {table} WHERE {ID_fieldname} = ?', (id,))



#---------[other]---------#

# generate an id
def gen_id():
    # use secrets module to generate a random 32-byte string
    return secrets.token_hex(32)
