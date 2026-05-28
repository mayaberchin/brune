import { useState, useEffect } from "react";
import PostEditor from "./components/PostEditor";
import PostPreview from "./components/PostPreview";
import PostView from "./components/PostView";
import PostLayout from "./layouts/PostLayout";

const root = document.getElementById("root");

const selectedPostType = root.dataset.postType;
const pageTitle = root.dataset.pageTitle;
const pageDescription = root.dataset.pageDescription;
const newPostLabel = root.dataset.newPostLabel;
const canPost = root.dataset.canPost === "yes";

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

    if (!response.ok) {
      alert(data.error);
      return;
    }

    // crete array w/ newest post in front
    setPosts([data.post, ...posts]);
    setShowPostEditor(false);
  }

  return (
    <PostLayout
      pageTitle={pageTitle}
      pageDescription={pageDescription}
      newPostLabel={newPostLabel}
      selectedPostType={selectedPostType}
      classes={testClasses}
      posts={posts}
      selectedPost={selectedPost}
      showPostEditor={showPostEditor}
      canPost={canPost}
      setSelectedPost={setSelectedPost}
      setShowPostEditor={setShowPostEditor}
      addPost={addPost}
    />
  );

}

export default App;
