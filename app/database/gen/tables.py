from datetime import datetime       # for dates/times

import helpers



#=====================================================[GLOBALS]=====================================================#



                                            #---------[table-columns]---------#


USERS_COLS = ['email', 'github', 'name', 'password_hash', 'is_dojo', 'is_sensei', 'is_stuy_teacher', 'class_id', 
              'unread_posts', 'pinged_posts']

CLASSES_COLS = ['class_id', 'name', 'owner_email', 'teacher_email', 'member_email', 'banned_email', 'posts', 
                'is_archived']

POSTS_COLS = ['post_id', 'author_email', 'class_id', 'parent_id', 'title', 'body', 'attachments', 'category', 
              'is_resolved','is_answer', 'created_at', 'updated_at', 'upvotes', 'upvoters', 'ping', 'show_dojo', 
              'is_anonymous']




#===================================================[MAKE-TABLES]===================================================#



                                            #---------individual]---------#
                                            
                                            
# users
def create_users_table():
    command =  """
                CREATE TABLE IF NOT EXISTS users (
                    email           TEXT        NOT NULL    PRIMARY KEY     UNIQUE,
                    github          TEXT,
                    name            TEXT        NOT NULL,
                    password_hash   TEXT        NOT NULL,
                    is_dojo         TEXT        NOT NULL,
                    is_sensei       TEXT        NOT NULL,
                    is_stuy_teacher TEXT        NOT NULL,
                    class_id        TEXT,
                    unread_posts    TEXT,
                    pinged_posts    TEXT
                )"""
    helpers.sqlite(command)

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
    helpers.sqlite(command)

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
                    created_at      TEXT        NOT NULL,
                    updated_at      TEXT        NOT NULL,
                    upvotes         INTEGER     NOT NULL,
                    upvoters        TEXT,
                    ping            TEXT,
                    show_dojo       TEXT        NOT NULL,
                    is_anonymous    TEXT        NOT NULL
                )"""
    helpers.sqlite(command)




                                            #---------[all]---------#


def create_tables():
    create_users_table()
    create_classes_table()
    create_posts_table()




#====================================================[ACCESSORS]====================================================#



                                            #---------[field]---------#


# PURPOSE
# Fetch a value or list of values from entries: identify entries where a certain field (column) matches a certain value (ID).

# PARAMETERS
# table             STRING          The name of the table to pull data from.
# ID_fieldname      STRING          The name of the field (column) whose value needs to match the ID.
# ID                ANY             Matches the value in the {ID_fieldname} column of an entry (row) containing data we want.
# field             STRING          The name of the field (column) containing the data we want.

# RETURN VALUES
# Use get_field() to get ONE piece of data from the table.
# Use get_field_list() to get all data matching the criteria from the table.


def get_field(table, ID_fieldname, ID, field):
    lst = get_field_list(table, ID_fieldname, ID, field)
    if (len(lst) == 0):
        return 'None'
    return lst[0]

def get_field_list(table, ID_fieldname, ID, field):
    # use ? for user-provided, potentially unsafe values
    data = helpers.sqlite_fetchall(f'SELECT {field} FROM {table} WHERE {ID_fieldname} = ?', (ID,))
    return helpers.clean_list(data)




                                            #---------[row]---------#


# PURPOSE
# Fetch a row (entry) or list of rows: identify rows where a certain field (column) matches a certain value (ID).

# PARAMETERS
# table             STRING          The name of the table to pull data from.
# ID_fieldname      STRING          The name of the field (column) whose value needs to match the ID.
# ID                ANY             Matches the value in the {ID_fieldname} column of an entry (row) containing data we want.

# RETURN VALUES
# Use get_row() to get ONE row of data (as a list) from the table.
# Use get_row_list() to get all rows (as a 2d list) matching the criteria from the table.


def get_row(table, ID_fieldname, ID):
    return get_row_list(table, ID_fieldname, ID)[0]

def get_row_list(table, ID_fieldname, ID):
    # use ? for user-provided, potentially unsafe values
    data = helpers.sqlite_fetchall(f'SELECT * FROM {table} WHERE {ID_fieldname} = ?', (ID,))
    return helpers.clean_2d_list(data)




                                            #---------[column]---------#


# PURPOSE
# Fetch an entire column of data from the table.

# PARAMETERS
# table             STRING          The name of the table to pull data from.
# col_name          STRING          The name of the column we want to fetch.

# RETURN VALUES
# get_col() returns a list of all items in the column.


def get_col(table, col_name):
    data = helpers.sqlite_fetchall(f'SELECT {col_name} FROM {table}')
    return helpers.clean_list(data)




#====================================================[MODIFIERS]====================================================#



                                            #---------[add]---------#


# PURPOSE
# Add a new entry (row) to a table.

# PARAMETERS
# table             STRING          The name of the table to add the entry to.
# vals              LIST-ANY        A list of values for each field (column) of the entry (row).

# RETURN VALUES
# add_row() returns nothing.


def add_row(table, vals):
    command = f'INSERT INTO {table} VALUES ('
    # use ? for user-provided, potentially unsafe values
    for i in range(len(vals)):
        command += '?,'
    command = command[:-1]
    command += ')'
    vals_tup= tuple(vals)
    helpers.sqlite(command, vals_tup)




                                            #---------[update]---------#


# PURPOSE
# Update a field (value) in an existing entry (row): identify this entry where a certain field (column) matches a certain value (ID).

# PARAMETERS
# table             STRING          The name of the table that contains the entry to modify.
# ID_fieldname      STRING          The name of the field (column) whose value needs to match the ID.
# ID                ANY             Matches the value in the {ID_fieldname} column of an entry (row) that we want to modify.
# col_name          STRING          The name of the field (column) whose value we want to update.
# item              ANY             The value we want to change the {col_name} field to.

# RETURN VALUES
# update_row() returns nothing.


def update_row(table, ID_fieldname, id, col_name, item):
    # use ? for user-provided, potentially unsafe values
    command = f'UPDATE {table} SET {col_name} = ? WHERE {ID_fieldname} = ?'
    vals = [item, id]
    vals_tup = tuple(vals)
    helpers.sqlite(command, vals_tup)




                                            #---------[delete]---------#


# PURPOSE
# Remove an entry (row) from a table: identify this entry where a certain field (column) matches a certain value (ID).

# PARAMETERS
# table             STRING          The name of the table that contains the entry to delete.
# ID_fieldname      STRING          The name of the field (column) whose value needs to match the ID.
# ID                ANY             Matches the value in the {ID_fieldname} column of an entry (row) that we want to delete.

# RETURN VALUES
# delete_row() returns nothing.


def delete_row(table, ID_fieldname, id):
    # use ? for user-provided, potentially unsafe values
    helpers.sqlite(f'DELETE FROM {table} WHERE {ID_fieldname} = ?', (id,))