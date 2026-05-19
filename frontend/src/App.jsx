import { useState } from "react";
import PostEditor from "./components/PostEditor";
import PostCard from "./components/PostCard";

const root = document.getElementById("root");
const selectedPostType = root.dataset.postType;
const pageTitle = root.dataset.pageTitle;
const pageDescription = root.dataset.pageDescription;
const newPostLabel = root.dataset.newPostLabel;

// get classes from flask later!
const testClasses = [
  { class_id: "1", name: "Software Development" },
  { class_id: "2", name: "Systems" },
  { class_id: "3", name: "Cybersecurity" },
];

function App() {
  const [showPostEditor, setShowPostEditor] = useState(false);
  const [posts, setPosts] = useState([]);

  function addPost(postData) {
    const newPost = {
      ...postData, // copies all fields from postData into newPost
      id: Date.now(), // post_id later!
    };

    // crete array w/ newest post in front
    setPosts([newPost, ...posts]);

    setShowPostEditor(false);
  }

  return (
    <main className="container py-4">
      <div className="d-flex justify-content-between align-items-start mb-4">
        <div>
          <h1>{pageTitle}</h1>
          <p className="text-muted mb-0">{pageDescription}</p>
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setShowPostEditor(true)}
        >
          + {newPostLabel}
        </button>
      </div>

      {showPostEditor && (
        <PostEditor
          selectedPostType={selectedPostType}
          classes={testClasses}
          onCancel={() => setShowPostEditor(false)}
          onSubmit={addPost}
        />
      )}

      <section className="mt-4">
        {posts.length === 0 ? (
          <p className="text-muted">No posts yet.</p>
        ) : (
          posts.map((post) => (
            <PostCard key={post.id} postData={post} />
          ))
        )}
      </section>

    </main>
  );
}

export default App;
