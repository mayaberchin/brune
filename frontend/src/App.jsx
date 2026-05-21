import { useState, useEffect } from "react";
import PostEditor from "./components/PostEditor";
import PostPreview from "./components/PostPreview";
import PostView from "./components/PostView";

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
  const [selectedPost, setSelectedPost] = useState(null);

  useEffect(() => { // runs after React renders the pg
    async function loadPosts() { // GET request fo Flask
      const response = await fetch(`/api/posts?category=${selectedPostType}`);
      const data = await response.json();
      setPosts(data.posts);
    }

    loadPosts();
  }, []);

  async function addPost(postData) {
    const response = await fetch("/api/posts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(postData),
    });
    const data = await response.json();

    // crete array w/ newest post in front
    setPosts([data.post, ...posts]);
    setShowPostEditor(false);
  }

  return (
    <main className="container py-4">

      {selectedPost === null && (
        <>
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
        </>
      )}

      <section className="mt-4">
        {selectedPost !== null ? ( // if not null show full post
          <PostView
            postData={selectedPost}
            onBack={() => setSelectedPost(null)}
          />
        ) : posts.length === 0 ? ( // if no post opened AND no posts
          <p className="text-muted">No posts yet.</p>
        ) : (
          posts.map((post) => ( // if no posts opened AND posts exist
            <PostPreview key={post.post_id} postData={post} onOpen={setSelectedPost} />
          )) // I feel like this should go in our code obfuscator its a miracle it worked...
        )}
      </section>

    </main>
  );
}

export default App;
