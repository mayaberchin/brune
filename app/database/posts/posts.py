from datetime import datetime               # for dates/times

import tables, helpers, users, classes

#---------[accessors]---------#


def get_all_posts():
    data = tables.get_col('posts', 'post_id')
    data = sort_by_ctime(data)
    return data

def get_posts_by(email):
    posts = get_all_posts()
    return [post for post in posts if get_post_author(post) == email]



def get_post_author(post_id):
    return get_posts_field(post_id, 'author_email')



def get_post_class(post_id):
    return get_posts_field(post_id, 'class_id')

def get_post_category(post_id):
    return get_posts_field(post_id, 'category')



def get_post_title(post_id):
    return get_posts_field(post_id, 'title')

def get_post_body(post_id):
    return get_posts_field(post_id, 'body')



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
    upvoters_lst = helpers.make_list(upvoters)
    return upvoters_lst

def get_post_pingees(post_id):
    ping = get_posts_field(post_id, 'ping')
    ping_lst = helpers.make_list(ping)
    # remove users who have been deleted since the last time this list was accessed
    ping_filtered = [user for user in ping_lst if users.user_exists(user)]
    ping_str = helpers.merge_list(ping_filtered)
    update_posts_row(post_id, 'ping', ping_str)
    return ping_filtered



def get_post_data(post_id):
    keys = POSTS_COLS
    values = tables.get_row('posts', 'post_id', post_id)
    d = helpers.list_to_dict(keys, values)
    d['attachments'] = helpers.make_list(d['attachments'])
    d['upvoters'] = helpers.make_list(d['upvoters'])
    d['ping'] = helpers.make_list(d['ping'])
    return d



#---------[modifiers]---------#



def change_post_title(post_id, new_title):
    update_posts_row(post_id, 'title', new_title)
    update_post_time(post_id)

def change_post_body(post_id, new_body):
    update_posts_row(post_id, 'body', new_body)
    update_post_time(post_id)



def update_post_time(post_id):
    time = str(datetime.now())
    update_posts_row(post_id, 'updated_at', time)



def increment_post_upvotes(post_id, inc):     # inc can be positive or negative
    upvotes = get_post_upvotes(post_id)
    upvotes += inc
    update_posts_row(post_id, 'upvotes', upvotes)

def add_post_upvoter(post_id, email):
    upvoters = get_post_upvoters(post_id)
    upvoters_new = helpers.add_to_list(upvoters, email)
    update_posts_row(post_id, 'upvoters', upvoters_new)
    increment_post_upvotes(post_id, 1)
    add_post_pingee(post_id, email)

def remove_post_upvoter(post_id, email):
    upvoters = get_post_upvoters(post_id)
    upvoters.remove(email)
    upvoters_new = helpers.merge_list(upvoters)
    update_posts_row(post_id, 'upvoters', upvoters_new)
    increment_post_upvotes(post_id, -1)
    remove_post_pingee(post_id, email)



def add_post_pingee(post_id, email):
    pingees = get_post_pingees(post_id)
    if email not in pingees:
        pingees_new = helpers.add_to_list(pingees, email)
        update_posts_row(post_id, 'ping', pingees_new)

def remove_post_pingee(post_id, email):
    author = get_post_author(post_id)
    if author != email:
        pingees = get_post_pingees(post_id)
        pingees.remove(email)
        pingees_new = helpers.merge_list(pingees)
        update_posts_row(post_id, 'ping', pingees_new)

def ping(post_id, pingees=[]):
    if len(pingees) == 0:
        pingees = get_post_pingees(post_id)
    for user in pingees:
        if not user_exists(user):
            remove_users += [user]
        else:
            pinged_posts = get_pinged_posts(user)
            pinged_str = helpers.add_to_list(pinged_posts, post_id)
            update_users_row(user, 'pinged_posts', pinged_str)


# decide to share post to dojo after post has already been created (this action cannot be undone)
def share_to_dojo(post_id):
    readers = get_all_dojo()
    for reader in readers:
        unread = get_unread_posts(reader)
        unread_str = helpers.add_to_list(unread, ping_post)
        update_users_row(reader, 'unread_posts', unread_str)
    update_posts_row(post_id, 'show_dojo', 'yes')


def get_all_unresolved():
    return [post for post in get_all_questions() if not post_is_resolved(post)]

def get_unresolved_posts(class_id):
    return [post for post in get_all_unresolved() if get_post_class(post) == class_id]

def post_is_resolved(post_id):
    is_resolved = get_posts_field(post_id, 'is_resolved')
    return is_resolved == 'yes'


def resolve_post(post_id):
    update_posts_row(post_id, 'is_resolved', 'yes')

def unresolve_post(post_id):
    update_posts_row(post_id, 'is_resolved', 'no')


#---------[creation-deletion]---------#


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
    c_posts_str = helpers.remove_from_list(class_posts, post_id)
    update_classes_row(class_id, 'posts', c_posts_str)
    # remove from users table
    readers = classes.get_class_members(class_id)
    if (show_dojo(post_id)):
        readers += users.get_all_dojo()
    readers = helpers.unique_only(readers)
    for reader in readers:
        users.mark_read(reader, post_id)    # removes the post from unread/ping
    # remove from posts table
    tables.delete_row('posts', 'post_id', post_id)


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

def get_posts_field_list(post_id, field_name):
    return get_field_list('posts', 'post_id', post_id, field_name)


def get_posts_row(post_id):
    return tables.get_row('posts', 'post_id', post_id)

def get_posts_row_list(post_id):
    return tables.get_row_list('posts', 'post_id', post_id)


def get_posts_col(col_name):
    return tables.get_col('posts', col_name)


def add_posts_row(values):
    add_row('posts', values)

def update_posts_row(post_id, col_name, value):
    update_row('posts', 'post_id', post_id, col_name, value)

def delete_posts_row(post_id):
    tables.delete_row('posts', 'post_id', post_id)