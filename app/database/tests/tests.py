import tables, helpers, users, classes, posts

if __name__ == "__main__":

    create_tables()

    add_user("mayaberchin@gmail.com", "hello", "Maya Berchin")
    add_user("other@gmail.com", "other", "Other Student")
    #print(str(get_all_users()))
    add_user("b@b.com", "b", "b b")

    #print(str(get_all_classes()))
    class_id = create_class("mayaberchin@gmail.com", "testclass")
    create_class("b@b.com", "dontjoin")
    print(class_id)
    #print("\n" + str(get_all_classes()))
    #print("Class teachers: " + str(get_class_teachers(class_id)))

    add_class_member(class_id, "other@gmail.com")

    print("\nClasses Maya is in: " + str(get_user_classes("mayaberchin@gmail.com")))
    print("Classes Maya teaches: " + str(get_teaching_classes("mayaberchin@gmail.com")))
    print("Classes Other is in: " + str(get_user_classes("other@gmail.com")))
    print("Classes Other teaches: " + str(get_teaching_classes("other@gmail.com")))


    #print("\nPromoting Other... also removing Maya as owner")
    promote_to_owner(class_id, 'other@gmail.com')
    demote_owner(class_id, "mayaberchin@gmail.com")

    print("Class teachers: " + str(get_class_teachers(class_id)))
    print("Classes Maya is in: " + str(get_user_classes("mayaberchin@gmail.com")))
    print("Classes Maya teaches: " + str(get_teaching_classes("mayaberchin@gmail.com")))
    print("Classes Other is in: " + str(get_user_classes("other@gmail.com")))
    print("Classes Other teaches: " + str(get_teaching_classes("other@gmail.com")))
    print("Classes Maya owns: " + str(get_owned_classes("mayaberchin@gmail.com")))
    print("Classes Other owns: " + str(get_owned_classes("other@gmail.com")))


    for i in range(15):
        add_user(f"{i}@gmail.com", "b", "b b")
        add_class_member(class_id, f'{i}@gmail.com')
    #print(str(get_class_members(class_id)))
    add_user("16@gmail.com", "b", "b b")
    add_user("17@gmail.com", "b", "b b")
    add_user("18@gmail.com", "b", "b b")
    add_class_member(class_id, '16@gmail.com')
    ban_member(class_id, '1@gmail.com')
    add_class_member(class_id, '17@gmail.com')
    #print(str(get_class_members(class_id)))
    add_class_member(class_id, '1@gmail.com')
    add_class_member(class_id, '18@gmail.com')
    #print(str(get_class_members(class_id)))
    change_class_name(class_id, "testingagain!")
    #print(get_class_name(class_id))
    archive_class(class_id)
    #print(str(get_active_classes()))
    un_archive_class(class_id)
    #print(str(get_active_classes()))

    #print("\n")
    #print(str(get_all_posts()))
    #delete_class(class_id)

    print(str(get_all_classes()))
    print("Classes Maya is in: " + str(get_user_classes("mayaberchin@gmail.com")))
    print("Classes Maya teaches: " + str(get_teaching_classes("mayaberchin@gmail.com")))
    print("Classes Other is in: " + str(get_user_classes("other@gmail.com")))
    print("Classes Other teaches: " + str(get_teaching_classes("other@gmail.com")))
    print("Classes Maya owns: " + str(get_owned_classes("mayaberchin@gmail.com")))
    print("Classes Other owns: " + str(get_owned_classes("other@gmail.com")))
    print(str(get_all_posts()))



    print("\n----------------------------------\n")
    # author_email, class_id, title, body, category, show_dojo, attachments='', is_anonymous='no', parent_id=''
    post_id = create_post("mayaberchin@gmail.com", class_id, "test_post", "this is the body of the test post", "question", "no")
    print(get_all_posts())
    print(str(get_post_data(post_id)))
    add_post_upvoter(post_id, "other@gmail.com")
    change_post_title(post_id, "test title 2")
    resolve_post(post_id)
    print(str(get_post_data(post_id)))
    unresolve_post(post_id)
    remove_post_upvoter(post_id, "other@gmail.com")
    add_post_upvoter(post_id, "b@b.com")
    share_to_dojo(post_id)
    print(str(get_post_data(post_id)))


    announcement_id = create_post("mayaberchin@gmail.com", class_id, "ann", "important announcement!", "announcement", "no")
    print("\n")
    print(announcement_id)
    print(str(get_unread_posts('0@gmail.com')))
    print(str(get_pinged_posts('0@gmail.com')))
    print(str(get_unresolved_posts(class_id)))

    create_followup('b@b.com', announcement_id, "huhhh???")
    create_followup('0@gmail.com', announcement_id, "lolll i get it")
    f_id = create_followup('0@gmail.com', announcement_id, ":)")
    print("parent: " + get_post_parent(f_id))
    add_post_upvoter(f_id, "b@b.com")
    fs = get_post_followups(announcement_id)['other']
    for f in fs:
        print(get_post_body(f))
    ff_id = create_followup('0@gmail.com', f_id, "double followup")
    ff_id = create_followup('0@gmail.com', f_id, "bleh")
    add_post_upvoter(ff_id, "b@b.com")
    ffs = get_post_followups(f_id)['other']
    for ff in ffs:
        print(get_post_body(ff))

    lst = get_teacher_head_posts(class_id)
    for item in lst:
        print(get_post_body(item))

    change_post_body(announcement_id, "nvm")
    print(str(get_post_data(announcement_id)))

    '''
    print("\n----------------------------------\n")
    add_senpai("mayaberchin@gmail.com")
    print(str(get_all_dojo()))
    '''