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


def create_post(author_email, class_id, title, body, category, show_dojo, attachments='', is_anonymous='no', parent_id=''):
    post_id = helpers.gen_id(get_all_posts(), 16)
    is_resolved = 'no'
    is_answer = 'no'
    time = str(datetime.now())
    upvotes = 0
    upvoters = ''
    to_ping = author_email
    add_posts_row([post_id, author_email, class_id, parent_id, title, body, attachments, category, is_resolved, is_answer, time, time, upvotes, upvoters, to_ping, show_dojo, is_anonymous])
    ping_post = get_top_parent(post_id)
    # add to classes table
    class_posts = classes.get_class_posts(class_id)
    posts_str = helpers.add_to_list(class_posts, ping_post)
    classes.update_classes_row(class_id, 'posts', posts_str)
    # add as unread post
    readers = classes.get_class_members(class_id)
    if (show_dojo == 'yes'):
        readers += users.get_all_dojo()
    readers = helpers.unique_only(readers)
    if author_email in readers:
        readers.remove(author_email)
    for reader in readers:
        unread = users.get_unread_posts(reader)
        unread_str = helpers.add_to_list(unread, ping_post)
        update_users_row(reader, 'unread_posts', unread_str)
    # ping necessary people
    if (parent_id != ''):
        ping(parent_id)
        add_post_pingee(parent_id, author_email)
    elif get_post_category(post_id) == 'announcement':
        ping_list = classes.get_class_members(class_id)
        if (show_dojo == 'yes'):
            ping_list += get_all_dojo()
        ping_list = helpers.unique_only(ping_list)
        ping_list.remove(author_email)
        ping(post_id, ping_list)
    return post_id