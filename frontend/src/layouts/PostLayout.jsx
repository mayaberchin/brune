import { useState } from "react";
import PostEditor from "../components/PostEditor";
import PostPreview from "../components/PostPreview";
import PostView from "../components/PostView";

function PostLayout({
  pageTitle,
  pageDescription,
  newPostLabel,
  selectedPostType,
  classes,
  posts,
  selectedPost,
  showPostEditor,
  setSelectedPost,
  setShowPostEditor,
  addPost,
}) {
  const [selectedClassId, setSelectedClassId] = useState("all"); // for course filter

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
            ) : (
              <button
                type="button"
                className="btn btn-primary btn-sm mt-2"
                onClick={() => setShowPostEditor(true)}
              >
                + {newPostLabel}
              </button>
            )}
            </div>

            {selectedPost === null && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setShowPostEditor(true)}
            >
              + {newPostLabel}
            </button>
          )}
        </div>

        {showPostEditor && (
          <PostEditor
            selectedPostType={selectedPostType}
            classes={classes}
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
          />
        ) : (
          <div className="class-filter-panel">
            <h2 className="h4">Courses</h2>

            <button
              type="button"
              className={selectedClassId === "all" ? "class-filter active" : "class-filter"}
              onClick={() => setSelectedClassId("all")}
            >
              All
            </button>

            {classes.map((classInfo) => (
              <button
                key={classInfo.class_id}
                type="button"
                className={
                  selectedClassId === String(classInfo.class_id)
                    ? "class-filter active"
                    : "class-filter"
                }
                onClick={() => setSelectedClassId(String(classInfo.class_id))}
              >
                {classInfo.name}
              </button>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default PostLayout;
