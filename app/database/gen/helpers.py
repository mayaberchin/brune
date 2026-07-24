import sqlite3                      # enable control of a sqlite database
import secrets                      # to generate ids


DB_FILE="../data.db"



#=======================================================[ID]=======================================================#



                                            #---------[generate]---------#


# PURPOSE
# Generate a unique id whenever needed.

# PARAMETERS
# others            LIST-STRINGS                        A list of previously used ids.
# byte_nums         INTEGER                             The number of bytes the id should take up.

# RETURN VALUES
# gen_id() returns a an alphanumeric string.


def gen_id(others, byte_nums):
    id = secrets.token_hex(byte_nums)
    while id in others:
        id = secrets.token_hex(byte_nums)
    return id




#=================================================[LIST-MANAGEMENT]=================================================#



                                            #---------[add/remove]---------#


# PURPOSE
# Add or remove an item from a list and convert the list into a delim-separated string.

# PARAMETERS
# lst               LIST-STRINGS or STRING              A list of items or a delim-separated string of items.
# item              STRING                              The item to add or remove.
# delim             STRING                              An optional delimeter; defaults to ','.          

# RETURN VALUES
# add_to_list() returns a delim-separated string with item appended.
# remove_from_list() returns a delim-separated string with (the first instance of) item removed.


def add_to_list(lst, item, delim=','):
    # check if lst has been provided as a list already or if we need to convert it into one
    if isinstance(lst, str):
        lst = make_list(lst, delim)
    lst.append(item)
    lst_str = merge_list(lst, delim)
    return lst_str

def remove_from_list(lst, item, delim=','):
    # check if lst has been provided as a list already or if we need to convert it into one
    if isinstance(lst, str):
        lst = make_list(lst, delim)
    if item in lst:
        lst.remove(item)
    lst_str = merge_list(lst, delim)
    return lst_str




                                            #---------[string-conversions]---------#


# PURPOSE
# Convert lists to/from delim-separated strings--we work with lists but store strings.

# PARAMETERS
# lst/str           LIST-STRINGS or STRING              The list/string to convert.
# delim             STRING                              An optional delimeter; defaults to ','.

# RETURN VALUES
# merge_list() returns a delim-separated string.
# make_list() returns a list.


def merge_list(lst, delim=','):
    if lst == None:
        return ''
    lst = rm_empty(lst)
    if lst == None:
        return ''
    return delim.join(lst)

def make_list(str, delim=','):
    if str == None:
        return []
    lst = str.split(delim)
    return rm_empty(lst)




                                            #---------[dictionary-conversions]---------#


# PURPOSE
# Convert plain lists into dictionaries, given a list of corresponding keys.

# PARAMETERS
# keys              LIST-STRINGS                                    A list of keys corresponding to the provided list of values.
# values            LIST-STRINGS or LIST-LIST-STRINGS               A list (or list of lists) of values corresponding to the provided list of keys.

# RETURN VALUES
# list_to_dict() returns a dictionary.
# list_2d_to_dict_list returns a list of dictionaries.


def list_to_dict(keys, values):
    if len(keys) != len(values):
        print("list_to_dict: len keys != len values")
        return {}
    dict = {}
    for i in range(len(keys)):
        dict[keys[i]] = values[i]
    return dict

def list_2d_to_dict_list(keys, values):
    lst = []
    for val_sublst in values:
        lst += [list_to_dict(keys, val_sublst)]
    return lst




                                            #---------[tuple conversions]---------#


# PURPOSE
# Convert a list of tuples (which is what is returned by .fetchall()) into lists to work with.
# Either create a 1d list or a 2d list.

# PARAMETERS
# raw_output        LIST-TUPLES             A list of tuples fetched as the result of a SQLite3 command.

# RETURN VALUES
# tups_to_list returns a 1d list.
# tups_to_list_2d returns a 2d list.


def tups_to_list(raw_output):
    lst = []
    for tup in raw_output:
        # represent None as '', otherwise add item to list as is
        lst += ['' if item is None else item for item in tup]
    return lst

def tups_to_2d_list(raw_output):
    lst = []
    for tup in raw_output:
        sub_lst = list(tup)
        # represent None as '', otherwise add item to list as is
        sub_lst = ['' if item is None else item for item in sub_lst]
        lst += [sub_lst]
    return lst




                                            #---------[tuple-to-list-filtering]---------#


# PURPOSE
# Convert a list of tuples (which is what is returned by .fetchall()) into FILTERED lists to work with.
# Either create a 1d list or a 2d list.

# PARAMETERS
# raw_output       LIST-TUPLES          A list of tuples fetched as the result of a SQLite3 command.

# RETURN VALUES
# clean_list() returns a 1d list not containing ''.
# clean_2d_list() returns a 2d list not containing [] (though sub-lists may contain '').
# deep_clean_list() returns a 2d list not containing [] AND its sub-lists will not contain ''.


def clean_list(raw_output):
    clean_output = tups_to_lst(raw_output)
    clean_output = rm_empty(raw_output)
    return clean_output

def clean_2d_list(raw_output):
    clean_output = tups_to_2d_lst(raw_output)
    clean_output = rm_empty_lists(clean_output)
    return clean_output

def deep_clean_list(raw_output):
    clean_output = tups_to_2d_list(raw_output)
    clean_output = deep_rm_empty(clean_output)
    return clean_output




                                            #---------[remove-empty]---------#


# PURPOSE
# Remove empty entries ('' or []) from lists.

# PARAMETERS
# lst(_2d)      LIST-STRINGS or LIST-LIST-STRINGS       The list to remove empty entries from.

# RETURN VALUES
# rm_empty() returns a 1d list not containing ''.
# rm_empty_lists() returns a 2d list not containing [] (though sub-lists may contain '').
# deep_rm_empty() returns a 2d list not containing [] AND its sub-lists will not contain ''.


def rm_empty(lst):
    clean_lst = [item for item in lst if item is not None and item != '']
    if (clean_lst is None):
        clean_lst = []
    return clean_lst

def rm_empty_lists(lst_2d):
    clean_lst = [lst for lst in lst_2d if len(lst) > 0]
    return clean_lst

def deep_rm_empty(lst_2d):
    new_lst = rm_empty_lists(lst_2d)
    for i in range(len(new_lst)):
        sub_lst = new_lst[i]
        new_lst[i] = rm_empty(sub_lst)
    return new_lst




                                            #---------[unique]---------#


# PURPOSE
# Return a list that only contains the unique values of the inputted list.

# PARAMETERS
# lst               LIST-ANY                            A list of any items.

# RETURN VALUES
# unique_only() returns a list of unique items.


def unique_only(lst):
    new_lst = []
    for item in lst:
        if item not in new_lst:
            new_lst.append(item)
    return new_lst




#=====================================================[SQLITE3]=====================================================#



                                            #---------[execute]---------#


# PURPOSE
# These helper functions serve to interact directly with SQLite3.

# PARAMETERS
# command       STRING          A command for SQLite3 to execute.
# vals          TUPLE           An OPTIONAL tuple of values that are filtered (in case of SQL injection), then added to the command.

# RETURN VALUES
# sqlite() returns nothing.
# sqlite_fetchone() returns one piece of data from the dataset as a result of the given Sqlite command.
# sqlite_fetchall() returns a list of tuples (a lot of data) as a result of the given Sqlite command.


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