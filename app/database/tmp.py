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
