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