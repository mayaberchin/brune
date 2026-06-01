import { useState } from "react";
import PostEditor from "../components/PostEditor";
import PostPreview from "../components/PostPreview";
import PostView from "../components/PostView";
import ClassFilter, { MobileClassFilter } from "../components/ClassFilter";

function PostLayout({
  pageTitle,
  pageDescription,
  newPostLabel,
  selectedPostType,
  classes,
  posts,
  selectedPost,
  showPostEditor,
  canPost,
  setSelectedPost,
  setShowPostEditor,
  addPost,
  onVote,
}) {
  const [selectedClassId, setSelectedClassId] = useState("all"); // for course filter
  const postClasses =
    selectedPostType === "announcement"
      ? classes.filter((classInfo) => classInfo.is_teacher)
      : classes;

  const filteredPosts =
    selectedClassId === "all"
      ? posts // show all posts
      : posts.filter((post) => String(post.class_id) === selectedClassId); // show filtered posts

  return (
    <main className={selectedPost === null ? "post-layout" : "post-layout has-open-post"}>
      <section className="post-list-panel">

        <div className="post-list-header">
          <div className="post-list-header-area">
            <h1>{pageTitle}</h1>

            {selectedPost === null ? (
              <p className="text-muted mb-0">{pageDescription}</p>
            ) : canPost && (
              <button
                type="button"
                className="btn btn-primary btn-sm mt-2"
                onClick={() => setShowPostEditor(true)}
              >
                + {newPostLabel}
              </button>
            )}
            </div>

            {selectedPost === null && canPost && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setShowPostEditor(true)}
            >
              + {newPostLabel}
            </button>
          )}
        </div>

        {selectedPost === null && (
          <MobileClassFilter
            classes={classes}
            selectedClassId={selectedClassId}
            setSelectedClassId={setSelectedClassId}
          />
        )}

        {showPostEditor && canPost && (
          <PostEditor
            selectedPostType={selectedPostType}
            classes={postClasses}
            onCancel={() => setShowPostEditor(false)}
            onSubmit={addPost}
          />
        )}

        {!showPostEditor && (
          <div className="post-preview-list">
            {filteredPosts.length === 0 ? (
              <p className="text-muted p-3">No posts yet.</p>
            ) : (
              filteredPosts.map((post) => (
                <PostPreview
                  key={post.post_id}
                  postData={post}
                  onOpen={setSelectedPost}
                  isSelected={selectedPost?.post_id === post.post_id}
                  showClass={selectedClassId === "all"}
                />
              ))
            )}
          </div>
        )}
      </section>

      <section className="post-side-panel">
        {selectedPost !== null ? (
          <PostView
            postData={selectedPost}
            onBack={() => setSelectedPost(null)}
            showClass={selectedClassId === "all"}
            onVote={onVote}
          />
        ) : (
          <ClassFilter
            classes={classes}
            selectedClassId={selectedClassId}
            setSelectedClassId={setSelectedClassId}
          />
        )}
      </section>
    </main>
  );
}

export default PostLayout;
