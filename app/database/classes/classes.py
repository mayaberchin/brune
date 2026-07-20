import tables, helpers, users, posts


#---------[accessors]---------#


def get_active_classes():
    classes = get_all_classes()
    return [c for c in classes if not is_archived(c)]

def get_all_classes():
    data = tables.get_col('classes', 'class_id')
    return data



def get_class_name(class_id):
    return get_classes_field(class_id, 'name')



def get_class_members(class_id):
    members_str = get_classes_field(class_id, 'member_email')
    members = helpers.make_list(members_str)
    return members

# get the teachers of a class
def get_class_teachers(class_id):
    teachers_str = get_classes_field(class_id, 'teacher_email')
    teachers = helpers.make_list(teachers_str)
    return teachers

def get_class_owners(class_id):
    owners_str = get_classes_field(class_id, 'owner_email')
    owners = helpers.make_list(owners_str)
    return owners

def get_banned_members(class_id):
    banned_str = get_classes_field(class_id, 'banned_email')
    banned = helpers.make_list(banned_str)
    return banned



def get_class_posts(class_id):
    data = get_classes_field(class_id, 'posts')
    posts = helpers.make_list(data)
    posts = posts.sort_by_ctime(posts)
    return posts

# return only top-level posts, not followups
def get_head_posts(class_id):
    posts = [post for post in get_class_posts(class_id) if posts.get_post_depth(post) == 0]
    posts = posts.sort_by_ctime(posts)
    return posts

def get_teacher_posts(class_id):
    posts = get_class_posts(class_id)
    teachers = get_class_teachers(class_id)
    t_posts = []
    for post in posts:
        if posts.get_post_author(post) in teachers:
            t_posts += [post]
    return t_posts

def get_teacher_head_posts(class_id):
    posts = posts.get_head_posts(class_id)
    teachers = get_class_teachers(class_id)
    t_posts = []
    for post in posts:
        if posts.get_post_author(post) in teachers:
            t_posts += [post]
    return t_posts

def get_class_announcements(class_id):
    posts = [post for post in posts.get_head_posts(class_id) if posts.get_post_category(post) == 'announcement']
    posts = posts.sort_by_ctime(posts)
    return posts

def get_class_questions(class_id):
    posts = [post for post in posts.get_head_posts(class_id) if posts.get_post_category(post) == 'question']
    posts = posts.sort_by_ctime(posts)
    return posts

def get_class_notes(class_id):
    posts = [post for post in posts.get_head_posts(class_id) if posts.get_post_category(post) == 'note']
    posts = posts.sort_by_ctime(posts)
    return posts

def get_class_n_gc(class_id, n=-1):
    posts = get_class_posts(class_id)
    posts = posts.sort_by_ctime(posts)
    gc = [post for post in posts if posts.get_post_category(post) == 'chat']
    if (n > 0):
        return gc[:n]
    return gc

def get_class_gc_by(class_id, email):
    posts = get_class_posts(class_id)
    posts = posts.sort_by_ctime(posts)
    gc = [post for post in posts if posts.get_post_category(post) == 'chat' and posts.get_post_author(post) == email]
    return gc


def get_class_data(class_id):
    keys = CLASSES_COLS
    values = get_classes_row('classes', 'class_id', class_id)
    d = helpers.list_to_dict(keys, values)
    d['teacher_email'] = helpers.make_list(d['teacher_email'])
    d['posts'] = helpers.make_list(d['posts'])
    d['posts'] = helpers.sort_by_ctime(d['posts'])
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
    class_id = helpers.gen_id(get_all_classes(), 3)
    owner = teacher_email
    members = teacher_email
    posts = ''
    is_archived = 'no'
    banned = ''
    add_classes_row([class_id, class_name, owner, teacher_email, members, banned, posts, is_archived])
    # add the class to teacher's users table
    teacher_classes = get_user_classes(teacher_email)
    teacher_classes_str = helpers.add_to_list(teacher_classes, class_id)
    update_users_row(teacher_email, 'class_id', teacher_classes_str)
    return class_id


def delete_class(class_id):
    members = get_class_members(class_id)
    for member in members:
        remove_member(class_id, member, True)
    delete_classes_row(class_id)


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
    classes = users.get_user_classes(email)
    classes_updated = helpers.add_to_list(classes, class_id)
    update_users_row(email, 'class_id', classes_updated)
    users = get_class_members(class_id)
    users_updated = helpers.add_to_list(users, email)
    update_classes_row(class_id, 'member_email', users_updated)
    return 'oke'



# promote a class member to a teacher for that class
def promote_to_teacher(class_id, email):
    teachers = get_class_teachers(class_id)
    teachers_str = helpers.add_to_list(teachers, email)
    update_classes_row(class_id, 'teacher_email', teachers_str)

# promote a class member to an owner for that class
def promote_to_owner(class_id, email):
    owners = get_class_owners(class_id)
    owners_str = helpers.add_to_list(owners, email)
    update_classes_row(class_id, 'owner_email', owners_str)
    # add them to teachers list if they aren't there yet
    if email not in get_class_teachers(class_id):
        promote_to_teacher(class_id, email)



def demote_teacher(class_id, email):
    teachers = get_class_teachers(class_id)
    teachers_str = helpers.remove_from_list(teachers, email)
    update_classes_row(class_id, 'teacher_email', teachers_str)

def demote_owner(class_id, email, leave_as_teacher=True):
    owners = get_class_owners(class_id)
    owners_str = helpers.remove_from_list(owners, email)
    update_classes_row(class_id, 'owner_email', owners_str)
    # demote from teacher role too
    if (not leave_as_teacher):
        demote_teacher(class_id, email)



def remove_member(class_id, email, purge_posts=False):
    # remove email from class owners list
    if (is_class_owner(class_id, email)):
        class_owners = get_class_owners(class_id)
        new_class_owners = helpers.remove_from_list(class_owners, email)
        update_classes_row(class_id, 'owner_email', new_class_owners)
    # remove email from class teachers list
    if (is_class_teacher(class_id, email)):
        class_teachers = get_class_teachers(class_id)
        new_class_teachers = helpers.remove_from_list(class_teachers, email)
        update_classes_row(class_id, 'teacher_email', new_class_teachers)
    # remove email from class members list
    class_members = get_class_members(class_id)
    new_class_members = helpers.remove_from_list(class_members, email)
    update_classes_row(class_id, 'member_email', new_class_members)
    # remove class from users class list
    user_classes = users.get_user_classes(email)
    new_user_classes = helpers.remove_from_list(user_classes, class_id)
    update_users_row(email, 'class_id', new_user_classes)
    # remove posts from this class in the user's table
    posts = get_class_posts(class_id)
    for post in posts:
        users.mark_read(email, post)
    # purge posts from this user if specified
    if (purge_posts):
        posts.delete_class_posts_by(class_id, email)


def ban_member(class_id, email, purge_posts=False):
    remove_member(class_id, email, purge_posts)
    banned = get_banned_members(class_id)
    banned_str = helpers.add_to_list(banned, email)
    update_classes_row(class_id, 'banned_email', banned_str)




#---------[classes-helpers]---------#


def get_classes_field(class_id, field_name):
    return tables.get_field('classes', 'class_id', class_id, field_name)

def get_classes_field_list(class_id, field_name):
    return tables.get_field_list('classes', 'class_id', class_id, field_name)
    

def get_classes_row(class_id):
    return tables.get_row('classes', 'class_id', class_id)

def get_classes_row_list(class_id):
    return tables.get_row_list('classes', 'class_id', class_id)
    

def get_classes_col(col_name):
    return tables.get_col('classes', col_name)
    

def add_classes_row(values):
    add_row('classes', values)

def update_classes_row(class_id, col_name, col_val):
    update_row('classes', 'class_id', class_id, col_name, col_val)

def delete_classes_row(class_id):
    tables.delete_row('classes', 'class_id', class_id)