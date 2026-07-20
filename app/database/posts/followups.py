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
            if classes.is_class_teacher(get_post_class(post), get_post_author(post)):
                teacher_answers += [post]
            else:
                answers += [post]
        elif classes.is_class_teacher(get_post_class(post), get_post_author(post)):
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

def post_is_answer(post_id):
    is_answer = get_posts_field(post_id, 'is_answer')
    return is_answer == 'yes'

def mark_post_as_answer(post_id):
    update_posts_row(post_id, 'is_answer', 'yes')

def unmark_post_as_answer(post_id):
    update_posts_row(post_id, 'is_answer', 'no')


def create_followup(author_email, post_id, body, is_anonymous='no'):
    followup_id = helpers.gen_id(get_all_posts(), 16)
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