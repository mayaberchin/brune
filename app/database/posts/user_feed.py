def get_pinged_posts(email):
    pinged_posts_str = get_users_field(email, 'pinged_posts')
    pinged_posts = helpers.make_list(pinged_posts_str)
    pinged_posts = posts.sort_by_ctime(pinged_posts)
    return pinged_posts

# returns unread posts from announcements, questions, and notes (but not groupchat) from any class
def get_top_n_pinged(email, n):
    all = get_pinged_posts(email)
    # prioritize announcements, then questions, then notes (don't get gc)
    announcements = []
    questions = []
    notes = []
    for post in all:
        type = posts.get_post_category(post)
        if type == 'announcement':
            announcements += [post]
        elif type == 'question':
            questions += [post]
        elif type == 'notes':
            notes += [post]
    ordered = announcements[:n]
    ordered += questions[:n-len(ordered)]
    ordered += notes[:n-len(ordered)]
    return ordered


def get_unread_posts(email):
    unread_posts_str = get_users_field(email, 'unread_posts')
    unread_posts = helpers.make_list(unread_posts_str)
    unread_posts = helpers.sort_by_ctime(unread_posts)
    return unread_posts

# returns unread posts from announcements, questions, and notes (but not groupchat) from any class
def get_top_n_unread(email, n):
    all = get_unread_posts(email)
    # prioritize announcements, then questions, then notes (don't get gc)
    announcements = []
    questions = []
    notes = []
    for post in all:
        type = posts.get_post_category(post)
        if type == 'announcement':
            announcements += [post]
        elif type == 'question':
            questions += [post]
        elif type == 'notes':
            notes += [post]
    ordered = announcements[:n]
    ordered += questions[:n-len(ordered)]
    ordered += notes[:n-len(ordered)]
    return ordered


# returns at most one message (if there is an unread one) from the groupchat of at most n classes
def get_top_n_gc(email, n):
    all = get_unread_posts(email)
    gc = [post for post in all if posts.get_post_category(post) == 'groupchat']
    messages = []
    classes = []
    while len(gc) > 0 and len(classes) < n:
        msg_class = posts.get_post_class(gc[-1])
        if msg_class not in classes:
            classes += msg_class
            messages += [{gc[-1]: msg_class}]
            gc.remove(gc[-1])
    messages = posts.sort_by_ctime(messages)
    return messages


# returns a dictionary of stuff to display on the homepage
def get_homepage_posts(email, n):
    # get a list of pinged posts
    pinged = get_top_n_pinged(email, n)
    # get a list of unread posts if there aren't enough pinged posts
    unread = []
    if len(pinged) < n:
        unread = get_top_n_unread(email, n-len(pinged))
    posts = {}
    posts['pinged'] = posts.sort_by_ctime(pinged)
    posts['unread'] = posts.sort_by_ctime(unread)
    return posts